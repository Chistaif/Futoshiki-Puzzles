"""
ForwardSolver — FOL Forward Chaining + Backtracking (MAC).
 
Kiến trúc 2 tầng:
  Tầng 1 — FC thuần (Modus Ponens):
    Xuất phát từ các facts ban đầu (Given, LessH, GreaterH, LessV, GreaterV),
    áp dụng 5 luật suy diễn liên tục cho đến khi không còn fact mới.
    Đây là bước "inference" đúng nghĩa FOL Forward Chaining.
 
  Tầng 2 — Backtracking (MAC):
    Khi FC bị kẹt (domain > 1, không mâu thuẫn), chọn ô chưa gán
    có domain nhỏ nhất (MRV), thử từng value, chạy FC sau mỗi lần gán.
    Nếu FC phát hiện mâu thuẫn → backtrack, khôi phục domain và thử value khác.
 
5 Luật suy diễn (Modus Ponens):
  Luật 1: Assign(i,j,v)        → Remove(i,j,v') ∀v' ≠ v
  Luật 2: domain(i,j) = ∅      → Contradiction
  Luật 3: domain(i,j) = {v}    → Assign(i,j,v)
  Luật 4: Assign(i,j,v)        → Remove(i,c,v) ∀c≠j  (hàng)
                                → Remove(r,j,v) ∀r≠i  (cột)
  Luật 5: domain(i,j) thay đổi → lan truyền bất đẳng thức 4 hướng (AC-3)
"""
from collections import deque
from typing import Callable, Deque, List, Optional, Set, Tuple

from src.solvers.solver import MAX_NODES_FORWARD_CHAINING, Solver
from src.domain.puzzle import PuzzleCase

StepCallback = Callable[[int, int, int], None]
Fact         = Tuple   # ("Assign", i, j, val) | ("Remove", i, j, val)
Domains      = List[List[Set[int]]]


class ForwardSolver(Solver):
    """
    FOL Forward Chaining + Backtracking.

    FC đóng vai trò inference engine (propagate + detect contradiction).
    Backtracking đóng vai trò search engine (branch khi FC bị kẹt).
    Kết hợp = MAC (Maintaining Arc Consistency).
    """

    def __init__(self):
        super().__init__(name="Forward Chaining")
        self.max_nodes = MAX_NODES_FORWARD_CHAINING
        self.n         = 0
        self._puzzle   = None

    # =========================================================================
    # Public API
    # =========================================================================

    def solve(self, puzzle: PuzzleCase, step_callback: Optional[StepCallback] = None):
        self.n       = puzzle.n
        self._puzzle = puzzle

        # Khởi tạo domain: mỗi ô có thể nhận giá trị 1..N
        domains: Domains = [
            [set(range(1, self.n + 1)) for _ in range(self.n)]
            for _ in range(self.n)
        ]

        # ── Tầng 1: FC với facts ban đầu ─────────────────────────────────────
        ok = self._run_fc(domains, self._initial_facts(puzzle), step_callback)
        if not ok:
            return None

        # ── Kiểm tra FC thuần đã giải xong chưa ──────────────────────────────
        if self._is_solved(domains):
            return self._extract_grid(domains)

        # ── Tầng 2: Backtracking (MAC) ────────────────────────────────────────
        # FIX: bỏ tham số puzzle thừa, _backtrack dùng self._puzzle
        success = self._backtrack(domains, step_callback)
        if not success:
            return None

        return self._extract_grid(domains)

    # =========================================================================
    # Facts ban đầu
    # =========================================================================

    def _initial_facts(self, puzzle: PuzzleCase) -> List[Fact]:
        """
        Chuyển puzzle thành danh sách facts ban đầu theo FOL:
          Given(i,j,v)   → ("Assign", i, j, v)
          LessH(i,j)     → ("Remove", i, j, N) và ("Remove", i, j+1, 1)
          GreaterH(i,j)  → ("Remove", i, j, 1) và ("Remove", i, j+1, N)
          LessV(i,j)     → tương tự chiều dọc
          GreaterV(i,j)  → tương tự chiều dọc
        """
        facts: List[Fact] = []

        # Given clues
        for i in range(self.n):
            for j in range(self.n):
                if puzzle.grid[i][j] != 0:
                    facts.append(("Assign", i, j, puzzle.grid[i][j]))

        # Horizontal inequalities
        for i in range(self.n):
            for j in range(self.n - 1):
                sign = puzzle.horizontal[i][j]
                if sign == 1:    # LessH(i,j): (i,j) < (i,j+1)
                    facts.append(("Remove", i, j,     self.n))
                    facts.append(("Remove", i, j + 1, 1))
                elif sign == -1: # GreaterH(i,j): (i,j) > (i,j+1)
                    facts.append(("Remove", i, j,     1))
                    facts.append(("Remove", i, j + 1, self.n))

        # Vertical inequalities
        for i in range(self.n - 1):
            for j in range(self.n):
                sign = puzzle.vertical[i][j]
                if sign == 1:    # LessV(i,j): (i,j) < (i+1,j)
                    facts.append(("Remove", i,     j, self.n))
                    facts.append(("Remove", i + 1, j, 1))
                elif sign == -1: # GreaterV(i,j): (i,j) > (i+1,j)
                    facts.append(("Remove", i,     j, 1))
                    facts.append(("Remove", i + 1, j, self.n))

        return facts

    # =========================================================================
    # Tầng 1 — FC Engine (Modus Ponens)
    # =========================================================================

    def _run_fc(
        self,
        domains:       Domains,
        initial_facts: List[Fact],
        step_callback: Optional[StepCallback] = None,
    ) -> bool:
        """
        Chạy FC cho đến khi agenda rỗng hoặc phát hiện contradiction.
        """
        agenda:     Deque[Fact] = deque()
        agenda_set: Set[Fact]   = set()
        propagated: Set[Tuple[int, int]] = set()

        def push(fact: Fact) -> None:
            if fact not in agenda_set:
                agenda.append(fact)
                agenda_set.add(fact)

        for fact in initial_facts:
            push(fact)

        while agenda:
            self.increment_nodes()

            if self.has_exceeded_max_nodes():
                return False

            fact = agenda.popleft()
            agenda_set.discard(fact)
            action = fact[0]

            # ── Rule 1 + 4: xử lý Assign ─────────────────────────────────────
            if action == "Assign":
                _, i, j, val = fact

                # val không còn trong domain → Contradiction
                if val not in domains[i][j]:
                    return False

                if (i, j) not in propagated:
                    propagated.add((i, j))
                    
                    # Cập nhật domain chốt ngay lập tức
                    domains[i][j] = {val}
                    
                    # Vẽ lên UI CHẮC CHẮN 100% được gọi khi ô có giá trị
                    if step_callback:
                        step_callback(i, j, val)
                        
                    # Lan truyền bất đẳng thức ngay lập tức
                    self._propagate_inequalities(i, j, domains, push)

                    # Lan truyền hàng và cột (Rule 4)
                    for c in range(self.n):
                        if c != j:
                            push(("Remove", i, c, val))
                    for r in range(self.n):
                        if r != i:
                            push(("Remove", r, j, val))

            # ── Rule 2 + 3 + 5: xử lý Remove ────────────────────────────────
            elif action == "Remove":
                _, i, j, val = fact

                if val not in domains[i][j]:
                    continue

                domains[i][j].discard(val)

                # Rule 2: domain rỗng → Contradiction
                if not domains[i][j]:
                    return False

                # Rule 3: domain còn 1 value → Assign
                if len(domains[i][j]) == 1:
                    push(("Assign", i, j, next(iter(domains[i][j]))))

                # Rule 5: lan truyền bất đẳng thức 4 hướng
                self._propagate_inequalities(i, j, domains, push)

        return True

    # =========================================================================
    # Tầng 2 — Backtracking (MAC)
    # =========================================================================

    def _backtrack(
        self,
        domains:       Domains,
        step_callback: Optional[StepCallback] = None,
    ) -> bool:
        """
        MAC Backtracking: chọn ô (MRV) → thử value → chạy FC → đệ quy.
        """

        if self.has_exceeded_max_nodes():
            return False

        # Chọn ô chưa gán có domain nhỏ nhất
        cell = self._pick_unassigned_cell(domains)
        if cell is None:
            return True   # Tất cả ô đã gán -> thành công

        i, j = cell

        # Thử từng value trong domain theo thứ tự tăng dần
        for val in sorted(domains[i][j]):

            saved_domains = [
                [domains[r][c].copy() for c in range(self.n)]
                for r in range(self.n)
            ]

            # Gán thử val cho (i,j) → đưa vào FC như một fact mới
            ok = self._run_fc(
                domains,
                [("Assign", i, j, val)],
                step_callback,
            )

            if ok:
                # FC thành công → tiếp tục đệ quy
                if self._backtrack(domains, step_callback):
                    return True

            # Rollback: FC thất bại hoặc đệ quy thất bại
            if step_callback is not None:
                self._rollback_callback(domains, saved_domains, step_callback)

            # Khôi phục domains về trước khi thử val
            for r in range(self.n):
                for c in range(self.n):
                    domains[r][c] = saved_domains[r][c]

        return False   # Mọi value đều thất bại → backtrack lên tầng trên

    # =========================================================================
    # Helpers
    # =========================================================================

    def _pick_unassigned_cell(self, domains: Domains) -> Optional[Tuple[int, int]]:
        """
        MRV (Minimum Remaining Values): chọn ô chưa gán có domain nhỏ nhất.
        Ô đã gán khi domain = {v} (1 phần tử).
        Trả về None nếu tất cả ô đã gán.
        """
        best     = None
        best_len = self.n + 1

        for i in range(self.n):
            for j in range(self.n):
                d = len(domains[i][j])
                if d > 1 and d < best_len:
                    best_len = d
                    best     = (i, j)
                    if best_len == 2:
                        return best   # Không thể nhỏ hơn 2, dừng sớm

        return best

    def _propagate_inequalities(
        self,
        i:       int,
        j:       int,
        domains: Domains,
        push:    Callable[[Fact], None],
    ) -> None:
        """
        Rule 5: Sau khi domain(i,j) thay đổi, lan truyền sang 4 ô láng giềng
        dựa trên min/max hiện tại của domain(i,j).

        Nguyên lý:
          (i,j) < neighbor  →  neighbor > cur_min  →  loại v ≤ cur_min
          (i,j) > neighbor  →  neighbor < cur_max  →  loại v ≥ cur_max
          neighbor < (i,j)  →  neighbor < cur_max  →  loại v ≥ cur_max
          neighbor > (i,j)  →  neighbor > cur_min  →  loại v ≤ cur_min
        """
        if not domains[i][j]:
            return

        cur_min = min(domains[i][j])
        cur_max = max(domains[i][j])
        puzzle  = self._puzzle

        # ── Phải (j+1): sign = horizontal[i][j] ─────────────────────────────
        if j < self.n - 1:
            sign = puzzle.horizontal[i][j]
            if sign == 1:    # (i,j) < (i,j+1) → (i,j+1) > cur_min → loại v ≤ cur_min
                for v in list(domains[i][j + 1]):
                    if v <= cur_min:
                        push(("Remove", i, j + 1, v))
            elif sign == -1: # (i,j) > (i,j+1) → (i,j+1) < cur_max → loại v ≥ cur_max
                for v in list(domains[i][j + 1]):
                    if v >= cur_max:
                        push(("Remove", i, j + 1, v))

        # ── Trái (j-1): sign = horizontal[i][j-1] ───────────────────────────
        if j > 0:
            sign = puzzle.horizontal[i][j - 1]
            if sign == 1:    # (i,j-1) < (i,j) → (i,j-1) < cur_max → loại v ≥ cur_max
                for v in list(domains[i][j - 1]):
                    if v >= cur_max:
                        push(("Remove", i, j - 1, v))
            elif sign == -1: # (i,j-1) > (i,j) → (i,j-1) > cur_min → loại v ≤ cur_min
                for v in list(domains[i][j - 1]):
                    if v <= cur_min:
                        push(("Remove", i, j - 1, v))

        # ── Dưới (i+1): sign = vertical[i][j] ──────────────────────────────
        if i < self.n - 1:
            sign = puzzle.vertical[i][j]
            if sign == 1:    # (i,j) < (i+1,j) → (i+1,j) > cur_min → loại v ≤ cur_min
                for v in list(domains[i + 1][j]):
                    if v <= cur_min:
                        push(("Remove", i + 1, j, v))
            elif sign == -1: # (i,j) > (i+1,j) → (i+1,j) < cur_max → loại v ≥ cur_max
                for v in list(domains[i + 1][j]):
                    if v >= cur_max:
                        push(("Remove", i + 1, j, v))

        # ── Trên (i-1): sign = vertical[i-1][j] ────────────────────────────
        if i > 0:
            sign = puzzle.vertical[i - 1][j]
            if sign == 1:    # (i-1,j) < (i,j) → (i-1,j) < cur_max → loại v ≥ cur_max
                for v in list(domains[i - 1][j]):
                    if v >= cur_max:
                        push(("Remove", i - 1, j, v))
            elif sign == -1: # (i-1,j) > (i,j) → (i-1,j) > cur_min → loại v ≤ cur_min
                for v in list(domains[i - 1][j]):
                    if v <= cur_min:
                        push(("Remove", i - 1, j, v))

    def _rollback_callback(
        self,
        current_domains: Domains,
        saved_domains:   Domains,
        step_callback:   StepCallback,
    ) -> None:
        """
        Xóa trên UI các ô bị thay đổi trong nhánh thất bại.
        """
        for i in range(self.n):
            for j in range(self.n):
                cur_len  = len(current_domains[i][j])
                prev_len = len(saved_domains[i][j])

                if prev_len > 1 and cur_len <= 1:
                    step_callback(i, j, 0)
                
                # Nếu trước đó đã gán (len == 1) nhưng bị mâu thuẫn xóa rỗng (len == 0)
                # Cần vẽ lại số cũ để UI không bị mất số của Given clue
                elif prev_len == 1 and cur_len == 0:
                    step_callback(i, j, next(iter(saved_domains[i][j])))

    def _is_solved(self, domains: Domains) -> bool:
        """Kiểm tra tất cả ô đã có đúng 1 value."""
        return all(len(domains[i][j]) == 1
                   for i in range(self.n)
                   for j in range(self.n))

    def _extract_grid(self, domains: Domains) -> List[List[int]]:
        """Chuyển domains sang lưới 2 chiều."""
        return [
            [next(iter(domains[i][j])) for j in range(self.n)]
            for i in range(self.n)
        ]
    def run(self, case: PuzzleCase, step_callback=None, input_file=None, output_file=None):
        return super().run(
            case,
            step_callback=step_callback,
            input_file=input_file,
            output_file=output_file,
        )