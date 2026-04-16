import copy

from solvers.horn_converter import HornConverter
from solvers.solver import Solver
from solvers.utils import standardize_variables, subst, unify


class BackwardSolver(Solver):
    def solve(self, puzzle):
        converter = HornConverter(puzzle)
        kb = converter.build()

        self.n = puzzle.n
        self.grid = copy.deepcopy(puzzle.grid)

        if self._backtrack(kb):
            return self.grid
        return None

    def _find_empty(self):
        for i in range(self.n):
            for j in range(self.n):
                if self.grid[i][j] == 0:
                    return i, j
        return None

    def _is_valid_by_logic(self, kb, i: int, j: int, v: int) -> bool:
        goal = ("not_val", (i, j, v))
        for _ in self.fol_bc_ask(kb, goal):
            return False
        return True

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

    def _backtrack(self, kb) -> bool:
        self.increment_nodes()
        empty = self._find_empty()
        if empty is None:
            return True

        i, j = empty
        for v in range(1, self.n + 1):
            if not self._is_valid_by_logic(kb, i, j, v):
                continue

            self.grid[i][j] = v
            kb.facts.append(("val", (i, j, v)))

            if self._backtrack(kb):
                return True

            self.grid[i][j] = 0
            kb.facts.pop()

        return False
