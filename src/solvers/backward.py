import copy
from typing import Callable, Optional

from src.kb.horn_converter import HornClause, HornConverter
from src.solvers.solver import Solver
from src.solvers.utils import standardize_variables, subst, unify


StepCallback = Callable[[int, int, int], None]


class BackwardSolver(Solver):
    def solve(self, puzzle, step_callback: Optional[StepCallback] = None):
        converter = HornConverter(puzzle)
        kb = converter.build()

        self.n = puzzle.n
        self.grid = copy.deepcopy(puzzle.grid)

        if self._backtrack(kb, step_callback):
            return self.grid
        return None

    def _find_empty(self):
        for i in range(self.n):
            for j in range(self.n):
                if self.grid[i][j] == 0:
                    return i, j
        return None

    def _is_valid_by_logic(self, kb, i: int, j: int, v: int) -> bool:
        """Kiểm tra val(i,j,v) có nhất quán với KB không bằng cách BC.

        Cách làm đúng theo yêu cầu đề (chứng minh dựa vào val(i,j,?)):
        1. Thêm val(i,j,v) vào KB như một GIẢI THUYẾT (hypothesis).
        2. BC mục tiêu: chứng minh not_val(i,j,v) từ KB + giả thuyết.
           - Chứng minh được  → giả thuyết tự mâu thuẫn → v KHÔNG hợp lệ.
           - Không chứng minh → KB nhất quán với val(i,j,v) → v HỢP LỆ.
        3. Rút giả thuyết ra khỏi KB (không ảnh hưởng đến bước sau).

        Vì sao cần thêm giả thuyết trước?
        Khi val(i,j,v) có trong KB, các rule sau mới kích hoạt được:
          - cell_uniqueness: val(i,j,v) ∧ neq(v,v2) → not_val(i,j,v2)
          - horizontal:      less_h(i,j) ∧ val(i,j,v) → not_val(i,j+1,v2)
          - vertical:        less_v(i,j) ∧ val(i,j,v) → not_val(i+1,j,v2)
        Nếu bỏ qua bước này, BC chỉ dựa vào các ô đã gán trước đó,
        bỏ sót mâu thuẫn phát sinh từ chính ô (i,j) với các ô lân cận.
        """
        # Bước 1: Giả thuyết — gán tạm val(i,j,v) vào KB
        hypothesis = HornClause(head=("val", (i, j, v)))
        kb.facts.append(hypothesis)

        # Bước 2: BC — chứng minh not_val(i,j,v) có dẫn đến mâu thuẫn không?
        contradiction = False
        for _ in self.fol_bc_ask(kb, ("not_val", (i, j, v))):
            contradiction = True
            break

        # Bước 3: Rút giả thuyết ra (dù kết quả thế nào)
        kb.facts.pop()

        return not contradiction

    @staticmethod
    def _clause_to_rule(clause):
        """Chuẩn hóa clause về dạng (antecedents, consequent)."""
        if hasattr(clause, "head") and hasattr(clause, "body"):
            return tuple(clause.body), clause.head
        return tuple(), clause

    @staticmethod
    def fol_bc_ask(kb, goal):
        """Wrapper cho backward chaining."""
        yield from BackwardSolver.fol_bc_or(kb, goal, {})

    @staticmethod
    def fol_bc_or(kb, goal, theta):
        """OR-node trong SLD resolution."""
        if theta == "failure":
            return

        clauses = list(kb.facts) + list(kb.rules)
        for clause in clauses:
            antecedents, consequent = standardize_variables(
                BackwardSolver._clause_to_rule(clause)
            )
            if goal[0] != consequent[0]:
                continue

            theta_prime = unify(goal[1], consequent[1], theta)
            if theta_prime != "failure":
                yield from BackwardSolver.fol_bc_and(kb, antecedents, theta_prime)

    @staticmethod
    def fol_bc_and(kb, goals, theta):
        """AND-node trong SLD resolution."""
        if theta == "failure":
            return
        if not goals:
            yield theta
            return

        first, rest = goals[0], goals[1:]
        first = subst(theta, first)
        for theta_prime in BackwardSolver.fol_bc_or(kb, first, theta):
            yield from BackwardSolver.fol_bc_and(kb, rest, theta_prime)

    def _backtrack(self, kb, step_callback: Optional[StepCallback] = None) -> bool:
        self.increment_nodes()
        empty = self._find_empty()
        if empty is None:
            return True

        i, j = empty
        for v in range(1, self.n + 1):
            if not self._is_valid_by_logic(kb, i, j, v):
                continue

            self.grid[i][j] = v
            if step_callback is not None:
                step_callback(i, j, v)
            # Gán chính thức vào KB (dùng HornClause để nhất quán với _is_valid_by_logic)
            kb.facts.append(HornClause(head=("val", (i, j, v))))

            if self._backtrack(kb, step_callback):
                return True

            self.grid[i][j] = 0
            if step_callback is not None:
                step_callback(i, j, 0)
            kb.facts.pop()

        return False