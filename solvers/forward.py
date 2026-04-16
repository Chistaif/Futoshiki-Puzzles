from solvers.solver import Solver
from solvers.fol_kb import FOLKB
from collections import defaultdict, deque
import copy
from typing import Callable, Optional


StepCallback = Callable[[int, int, int], None]


class ForwardBacktrackSolver(Solver):
    def __init__(self):
        super().__init__(name="Forward Chaining (DPLL)")
        self.kb = None

    def solve(self, puzzle, step_callback: Optional[StepCallback] = None):
        """
        Thực hiện giải bài toán bằng thuật toán DPLL (Forward Chaining + Backtracking)
        Method này được gọi bởi self.run(puzzle) của class Solver
        """
        # 1. Khởi tạo Knowledge Base từ puzzle
        self.kb = FOLKB(puzzle)
        clauses = self.kb.build_KB()

        # Dùng frozenset để clause immutable, tránh mutation in-place
        clauses = [list(c) for c in clauses]

        # 2. Tạo agenda từ các unit clause ban đầu
        agenda = deque()
        for clause in clauses:
            if len(clause) == 1:
                agenda.append(clause[0])

        # 3. Bắt đầu thuật toán đệ quy DPLL
        result_model = self._dpll(clauses, agenda, {}, step_callback)

        return self._translate_model_to_grid(result_model) if result_model else None

    # --------------------------------------------------------------------------
    # Hàm tiện ích nội bộ
    # --------------------------------------------------------------------------

    @staticmethod
    def _build_index(clauses):
        """
        Xây dựng lại chỉ mục literal -> danh sách clause chứa nó.
        Gọi sau mỗi lần clauses thay đổi (deepcopy khi backtrack).
        Đây là fix cho Bug #1: literal_to_clauses không được đồng bộ với clauses.
        """
        index = defaultdict(list)
        for clause in clauses:
            for literal in clause:
                index[literal].append(clause)
        return index

    # --------------------------------------------------------------------------
    # Thuật toán DPLL
    # --------------------------------------------------------------------------

    def _dpll(self, clauses, agenda, model, step_callback: Optional[StepCallback] = None):
        """Đệ quy DPLL: propagate -> chọn biến -> branch -> backtrack"""
        # Fix #2: Chỉ đếm node tại đây (mỗi lần branch = 1 node)
        self.increment_nodes()

        # Bước 1: Unit Propagation (Forward Chaining)
        # Rebuild index từ clauses hiện tại để đảm bảo đồng bộ
        literal_to_clauses = self._build_index(clauses)
        if not self._propagate(clauses, literal_to_clauses, agenda, model, step_callback):
            return None

        # Bước 2: Kiểm tra hoàn thành — Fix #3: truyền clauses vào MRV
        unassigned_var = self._get_unassigned_variable(clauses, model)
        if unassigned_var is None:
            return model  # Tất cả biến đã gán -> thành công

        # Bước 3: Backtracking — deepcopy cả clauses lẫn model
        saved_clauses = copy.deepcopy(clauses)
        saved_model = model.copy()

        # Thử nhánh True (literal dương) qua agenda để propagate xử lý đầy đủ
        result = self._dpll(clauses, deque([unassigned_var]), model, step_callback)
        if result:
            return result

        # Quay lui, thử nhánh False (literal âm = True)
        if step_callback is not None:
            for literal in self._model_positive_deltas(model, saved_model):
                decoded = self._decode_positive_literal(literal)
                if decoded is None:
                    continue
                row, col, _ = decoded
                step_callback(row, col, 0)

        clauses[:] = saved_clauses   # restore in-place để giữ reference
        model.clear()
        model.update(saved_model)
        neg_var = -unassigned_var
        # Không gán trực tiếp model; để propagate gán và simplify nhất quán
        return self._dpll(clauses, deque([neg_var]), model, step_callback)

    def _propagate(self, clauses, literal_to_clauses, agenda, model, step_callback: Optional[StepCallback] = None):
        """
        Unit Propagation — cốt lõi Forward Chaining.
        Nhận literal_to_clauses được build từ clauses hiện tại
        """
        while agenda:
            p = agenda.popleft()
            neg_p = -p

            # Mâu thuẫn: p và -p cùng được gán True
            if neg_p in model:
                return False

            if p not in model:
                model[p] = True
                if step_callback is not None:
                    decoded = self._decode_positive_literal(p)
                    if decoded is not None:
                        row, col, value = decoded
                        step_callback(row, col, value)

                # Xét các clause chứa -p: bỏ -p ra khỏi clause (đã biết False)
                for clause in list(literal_to_clauses.get(neg_p, [])):
                    if neg_p in clause:
                        clause.remove(neg_p)
                        if len(clause) == 0:
                            return False  # Clause rỗng -> mâu thuẫn
                        if len(clause) == 1:
                            unit = clause[0]
                            if unit not in model and unit not in agenda:
                                agenda.append(unit)

                # Xoá các clause chứa p (đã thoả mãn, không cần xét nữa)
                for clause in list(literal_to_clauses.get(p, [])):
                    if clause in clauses:
                        clauses.remove(clause)

        return True

    @staticmethod
    def _model_positive_deltas(model, saved_model):
        current_positive = {lit for lit in model if lit > 0 and model.get(lit) is True}
        saved_positive = {lit for lit in saved_model if lit > 0 and saved_model.get(lit) is True}
        return current_positive - saved_positive

    def _decode_positive_literal(self, literal):
        if literal <= 0:
            return None
        max_var = self.kb.n ** 3
        if literal > max_var:
            return None

        var_id = literal - 1
        row = var_id // (self.kb.n * self.kb.n)
        rem = var_id % (self.kb.n * self.kb.n)
        col = rem // self.kb.n
        value = rem % self.kb.n + 1
        return row, col, value

    def _get_unassigned_variable(self, clauses, model):
        """
        Clause ngắn nhất = bị ràng buộc nhiều nhất -> giải quyết sớm giảm backtrack.
        """
        shortest = None
        for clause in clauses:
            unassigned = [lit for lit in clause if lit not in model and -lit not in model]
            if not unassigned:
                continue
            if shortest is None or len(unassigned) < len(shortest):
                shortest = unassigned

        # Trả về literal dương đầu tiên trong clause ngắn nhất
        if shortest:
            lit = shortest[0]
            return lit if lit > 0 else -lit

        return None  # Tất cả đã gán

    def _translate_model_to_grid(self, model):
        """Chuyển Model logic sang mảng 2 chiều Puzzle"""
        grid = [[0] * self.kb.n for _ in range(self.kb.n)]
        for i in range(self.kb.n):
            for j in range(self.kb.n):
                for v in range(1, self.kb.n + 1):
                    if model.get(self.kb.var(i, j, v)) is True:
                        grid[i][j] = v
                        break
        return grid