from src.solvers.solver import Solver
from src.kb.fol_kb import FOLKB
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
        Thá»±c hiá»‡n giáº£i bÃ i toÃ¡n báº±ng thuáº­t toÃ¡n DPLL (Forward Chaining + Backtracking)
        Method nÃ y Ä‘Æ°á»£c gá»i bá»Ÿi self.run(puzzle) cá»§a class Solver
        """
        # 1. Khá»Ÿi táº¡o Knowledge Base tá»« puzzle
        self.kb = FOLKB(puzzle)
        clauses = self.kb.build_KB()

        # DÃ¹ng frozenset Ä‘á»ƒ clause immutable, trÃ¡nh mutation in-place
        clauses = [list(c) for c in clauses]

        # 2. Táº¡o agenda tá»« cÃ¡c unit clause ban Ä‘áº§u
        agenda = deque()
        for clause in clauses:
            if len(clause) == 1:
                agenda.append(clause[0])

        # 3. Báº¯t Ä‘áº§u thuáº­t toÃ¡n Ä‘á»‡ quy DPLL
        result_model = self._dpll(clauses, agenda, {}, step_callback)

        return self._translate_model_to_grid(result_model) if result_model else None

    # --------------------------------------------------------------------------
    # HÃ m tiá»‡n Ã­ch ná»™i bá»™
    # --------------------------------------------------------------------------

    @staticmethod
    def _build_index(clauses):
        """
        XÃ¢y dá»±ng láº¡i chá»‰ má»¥c literal -> danh sÃ¡ch clause chá»©a nÃ³.
        Gá»i sau má»—i láº§n clauses thay Ä‘á»•i (deepcopy khi backtrack).
        ÄÃ¢y lÃ  fix cho Bug #1: literal_to_clauses khÃ´ng Ä‘Æ°á»£c Ä‘á»“ng bá»™ vá»›i clauses.
        """
        index = defaultdict(list)
        for clause in clauses:
            for literal in clause:
                index[literal].append(clause)
        return index

    # --------------------------------------------------------------------------
    # Thuáº­t toÃ¡n DPLL
    # --------------------------------------------------------------------------

    def _dpll(self, clauses, agenda, model, step_callback: Optional[StepCallback] = None):
        """Äá»‡ quy DPLL: propagate -> chá»n biáº¿n -> branch -> backtrack"""
        # Fix #2: Chá»‰ Ä‘áº¿m node táº¡i Ä‘Ã¢y (má»—i láº§n branch = 1 node)
        self.increment_nodes()

        # BÆ°á»›c 1: Unit Propagation (Forward Chaining)
        # Rebuild index tá»« clauses hiá»‡n táº¡i Ä‘á»ƒ Ä‘áº£m báº£o Ä‘á»“ng bá»™
        literal_to_clauses = self._build_index(clauses)
        if not self._propagate(clauses, literal_to_clauses, agenda, model, step_callback):
            return None

        # BÆ°á»›c 2: Kiá»ƒm tra hoÃ n thÃ nh â€” Fix #3: truyá»n clauses vÃ o MRV
        unassigned_var = self._get_unassigned_variable(clauses, model)
        if unassigned_var is None:
            return model  # Táº¥t cáº£ biáº¿n Ä‘Ã£ gÃ¡n -> thÃ nh cÃ´ng

        # BÆ°á»›c 3: Backtracking â€” deepcopy cáº£ clauses láº«n model
        saved_clauses = copy.deepcopy(clauses)
        saved_model = model.copy()

        # Thá»­ nhÃ¡nh True (literal dÆ°Æ¡ng) qua agenda Ä‘á»ƒ propagate xá»­ lÃ½ Ä‘áº§y Ä‘á»§
        result = self._dpll(clauses, deque([unassigned_var]), model, step_callback)
        if result:
            return result

        # Quay lui, thá»­ nhÃ¡nh False (literal Ã¢m = True)
        if step_callback is not None:
            for literal in self._model_positive_deltas(model, saved_model):
                decoded = self._decode_positive_literal(literal)
                if decoded is None:
                    continue
                row, col, _ = decoded
                step_callback(row, col, 0)

        clauses[:] = saved_clauses   # restore in-place Ä‘á»ƒ giá»¯ reference
        model.clear()
        model.update(saved_model)
        neg_var = -unassigned_var
        # KhÃ´ng gÃ¡n trá»±c tiáº¿p model; Ä‘á»ƒ propagate gÃ¡n vÃ  simplify nháº¥t quÃ¡n
        return self._dpll(clauses, deque([neg_var]), model, step_callback)

    def _propagate(self, clauses, literal_to_clauses, agenda, model, step_callback: Optional[StepCallback] = None):
        """
        Unit Propagation â€” cá»‘t lÃµi Forward Chaining.
        Nháº­n literal_to_clauses Ä‘Æ°á»£c build tá»« clauses hiá»‡n táº¡i
        """
        while agenda:
            p = agenda.popleft()
            neg_p = -p

            # MÃ¢u thuáº«n: p vÃ  -p cÃ¹ng Ä‘Æ°á»£c gÃ¡n True
            if neg_p in model:
                return False

            if p not in model:
                model[p] = True
                if step_callback is not None:
                    decoded = self._decode_positive_literal(p)
                    if decoded is not None:
                        row, col, value = decoded
                        step_callback(row, col, value)

                # XÃ©t cÃ¡c clause chá»©a -p: bá» -p ra khá»i clause (Ä‘Ã£ biáº¿t False)
                for clause in list(literal_to_clauses.get(neg_p, [])):
                    if neg_p in clause:
                        clause.remove(neg_p)
                        if len(clause) == 0:
                            return False  # Clause rá»—ng -> mÃ¢u thuáº«n
                        if len(clause) == 1:
                            unit = clause[0]
                            if unit not in model and unit not in agenda:
                                agenda.append(unit)

                # XoÃ¡ cÃ¡c clause chá»©a p (Ä‘Ã£ thoáº£ mÃ£n, khÃ´ng cáº§n xÃ©t ná»¯a)
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
        Clause ngáº¯n nháº¥t = bá»‹ rÃ ng buá»™c nhiá»u nháº¥t -> giáº£i quyáº¿t sá»›m giáº£m backtrack.
        """
        shortest = None
        for clause in clauses:
            unassigned = [lit for lit in clause if lit not in model and -lit not in model]
            if not unassigned:
                continue
            if shortest is None or len(unassigned) < len(shortest):
                shortest = unassigned

        # Tráº£ vá» literal dÆ°Æ¡ng Ä‘áº§u tiÃªn trong clause ngáº¯n nháº¥t
        if shortest:
            lit = shortest[0]
            return lit if lit > 0 else -lit

        return None  # Táº¥t cáº£ Ä‘Ã£ gÃ¡n

    def _translate_model_to_grid(self, model):
        """Chuyá»ƒn Model logic sang máº£ng 2 chiá»u Puzzle"""
        grid = [[0] * self.kb.n for _ in range(self.kb.n)]
        for i in range(self.kb.n):
            for j in range(self.kb.n):
                for v in range(1, self.kb.n + 1):
                    if model.get(self.kb.var(i, j, v)) is True:
                        grid[i][j] = v
                        break
        return grid
