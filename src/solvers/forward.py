from src.solvers.solver import Solver
from src.kb.fol_kb import FOLKB
from collections import defaultdict, deque
from typing import Callable, List, Optional


StepCallback = Callable[[int, int, int], None]


class ForwardBacktrackSolver(Solver):
    def __init__(self):
        super().__init__(name="Forward Chaining (DPLL)")
        self.kb = None
        self.max_var = 0
        self.literal_frequency = None

    def solve(self, puzzle, step_callback: Optional[StepCallback] = None):
        self.kb = FOLKB(puzzle)
        clauses = self.kb.build_KB()
        clauses = [list(c) for c in clauses]

        self.max_var = self.kb.n ** 3
        literal_to_clauses = self._build_index(clauses)
        self.literal_frequency = self._count_literal_frequency(clauses)
        model = [0] * (self.max_var + 1)

        agenda = deque()
        agenda_set = set()
        for clause in clauses:
            if len(clause) == 1:
                unit = clause[0]
                if unit not in agenda_set:
                    agenda.append(unit)
                    agenda_set.add(unit)

        result_model = self._dpll(
            clauses,
            literal_to_clauses,
            agenda,
            agenda_set,
            model,
            step_callback,
        )
        return self._translate_model_to_grid(result_model) if result_model else None

    # --------------------------------------------------------------------------
    # Hàm tiện ích nội bộ
    # --------------------------------------------------------------------------

    @staticmethod
    def _build_index(clauses):
        index = defaultdict(list)
        for clause in clauses:
            for literal in clause:
                index[literal].append(clause)
        return index

    @staticmethod
    def _count_literal_frequency(clauses):
        frequency = defaultdict(int)
        for clause in clauses:
            for literal in clause:
                frequency[abs(literal)] += 1
        return frequency

    # --------------------------------------------------------------------------
    # Thuật toán DPLL
    # --------------------------------------------------------------------------

    def _dpll(
        self,
        clauses,
        literal_to_clauses,
        agenda,
        agenda_set,
        model,
        step_callback: Optional[StepCallback] = None,
    ):
        self.increment_nodes()

        if not self._propagate(clauses, literal_to_clauses, agenda, agenda_set, model, step_callback):
            return None

        unassigned_var = self._get_unassigned_variable(model)
        if unassigned_var is None:
            return model

        saved_model = model.copy()

        result = self._dpll(
            clauses,
            literal_to_clauses,
            deque([unassigned_var]),
            {unassigned_var},
            model,
            step_callback,
        )
        if result:
            return result

        if step_callback is not None:
            for var_id in range(1, self.max_var + 1):
                if model[var_id] != saved_model[var_id] and model[var_id] == 1:
                    decoded = self._decode_literal(var_id)
                    if decoded is not None:
                        step_callback(decoded[0], decoded[1], 0)

        model[:] = saved_model

        neg_var = -unassigned_var
        return self._dpll(
            clauses,
            literal_to_clauses,
            deque([neg_var]),
            {neg_var},
            model,
            step_callback,
        )

    def _propagate(
        self,
        clauses,
        literal_to_clauses,
        agenda,
        agenda_set,
        model,
        step_callback: Optional[StepCallback] = None,
    ):
        while agenda:
            p = agenda.popleft()
            agenda_set.discard(p)
            if self._is_false_literal(p, model):
                return False

            if not self._is_true_literal(p, model):
                self._assign_literal(p, model)
                if step_callback is not None and p > 0:
                    decoded = self._decode_literal(p)
                    if decoded:
                        step_callback(decoded[0], decoded[1], decoded[2])

            for clause in literal_to_clauses.get(-p, []):
                is_satisfied = False
                unassigned_count = 0
                unit_literal = 0

                for lit in clause:
                    if self._is_true_literal(lit, model):
                        is_satisfied = True
                        break
                    if not self._is_assigned(abs(lit), model):
                        unassigned_count += 1
                        unit_literal = lit
                        if unassigned_count > 1:
                            break

                if is_satisfied:
                    continue
                if unassigned_count == 0:
                    return False
                if unassigned_count == 1 and unit_literal not in agenda_set:
                    agenda.append(unit_literal)
                    agenda_set.add(unit_literal)
        return True

    def _assign_literal(self, literal, model):
        model[abs(literal)] = 1 if literal > 0 else -1

    def _is_assigned(self, var_id, model):
        return model[var_id] != 0

    def _is_true_literal(self, literal, model):
        if literal > 0:
            return model[abs(literal)] == 1
        return model[abs(literal)] == -1

    def _is_false_literal(self, literal, model):
        if literal > 0:
            return model[abs(literal)] == -1
        return model[abs(literal)] == 1

    def _decode_literal(self, literal: int):
        if literal <= 0:
            return None
        n = self.kb.n
        max_var = n ** 3
        if literal > max_var:
            return None

        zero_based = literal - 1
        row = zero_based // (n * n)
        rem = zero_based % (n * n)
        col = rem // n
        value = rem % n + 1
        return row, col, value

    def _get_unassigned_variable(self, model):
        n = self.kb.n
        best_literal = None
        best_domain_size = None
        best_frequency = -1

        for i in range(n):
            for j in range(n):
                cell_assigned = False
                for v in range(1, n + 1):
                    if model[self.kb.var(i, j, v)] == 1:
                        cell_assigned = True
                        break
                if cell_assigned:
                    continue

                domain_literals = []
                for v in range(1, n + 1):
                    var_id = self.kb.var(i, j, v)
                    if model[var_id] != -1:
                        domain_literals.append(var_id)

                if not domain_literals:
                    continue

                domain_size = len(domain_literals)
                literal = max(domain_literals, key=lambda lit: self.literal_frequency.get(lit, 0))
                frequency = self.literal_frequency.get(literal, 0)

                if best_domain_size is None:
                    best_domain_size = domain_size
                    best_literal = literal
                    best_frequency = frequency
                elif domain_size < best_domain_size:
                    best_domain_size = domain_size
                    best_literal = literal
                    best_frequency = frequency
                elif domain_size == best_domain_size and frequency > best_frequency:
                    best_literal = literal
                    best_frequency = frequency

        return best_literal

    def _translate_model_to_grid(self, model):
        grid = [[0] * self.kb.n for _ in range(self.kb.n)]
        for i in range(self.kb.n):
            for j in range(self.kb.n):
                for v in range(1, self.kb.n + 1):
                    if model[self.kb.var(i, j, v)] == 1:
                        grid[i][j] = v
                        break
        return grid
