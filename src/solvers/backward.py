import copy
from typing import Callable, Optional, Dict, List, Tuple

from src.kb.horn_converter import HornClause, HornConverter
from src.solvers.solver import MAX_NODES_BACKWARD_CHAINING, Solver
from src.solvers.utils import subst, unify, is_variable

StepCallback = Callable[[int, int, int], None]


# ==========================================
# UTIL
# ==========================================

def is_ground_expr(expr):
    if is_variable(expr):
        return False
    if isinstance(expr, (tuple, list)):
        return all(is_ground_expr(e) for e in expr)
    return True


class BackwardSolver(Solver):
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self.max_nodes = MAX_NODES_BACKWARD_CHAINING
        self.memo = {}
        self.kb_version = 0
        self.found_solution = False
        self.fact_index: Dict[str, List[HornClause]] = {}
        self.val_fact_cell_index: Dict[Tuple[int, int], List[HornClause]] = {}
        self.val_rule_cell_index: Dict[Tuple[int, int], List[HornClause]] = {}
        self.val_rule_generic: List[HornClause] = []

    # ==========================================
    # FACT INDEX
    # ==========================================

    def _index_add(self, clause: HornClause):
        self.fact_index.setdefault(clause.head[0], []).append(clause)
        if clause.head[0] == "val":
            i, j, _ = clause.head[1]
            if not is_variable(i) and not is_variable(j):
                self.val_fact_cell_index.setdefault((i, j), []).append(clause)

    def _index_remove(self, clause: HornClause):
        self.fact_index[clause.head[0]].pop()
        if clause.head[0] == "val":
            i, j, _ = clause.head[1]
            if not is_variable(i) and not is_variable(j):
                self.val_fact_cell_index[(i, j)].pop()

    def _rebuild_fact_index(self, kb):
        self.fact_index = {}
        self.val_fact_cell_index = {}
        for clause in kb.facts:
            self._index_add(clause)

    def _rebuild_val_rule_index(self, kb):
        self.val_rule_cell_index = {}
        self.val_rule_generic = []

        for rule in kb.rules:
            if rule.head[0] != "val":
                continue
            i, j, _ = rule.head[1]
            if is_variable(i) or is_variable(j):
                self.val_rule_generic.append(rule)
            else:
                self.val_rule_cell_index.setdefault((i, j), []).append(rule)

    # ==========================================
    # SOLVE
    # ==========================================

    def solve(self, puzzle, step_callback: Optional[StepCallback] = None, **kwargs):
        converter = HornConverter(puzzle)
        kb = converter.build()

        self.n = puzzle.n
        self.grid = copy.deepcopy(puzzle.grid)
        self.found_solution = False
        self.memo = {}
        self.kb_version = 0

        # Domain
        for v in range(1, self.n + 1):
            kb.facts.append(HornClause(head=("domain", (v,))))

        # Given
        for r in range(self.n):
            for c in range(self.n):
                if self.grid[r][c] != 0:
                    kb.facts.append(HornClause(head=("val", (r, c, self.grid[r][c]))))

        # Generator rules
        for v in range(1, self.n + 1):
            kb.rules.append(HornClause(
                head=("val", ('i', 'j', v)),
                body=[("domain", (v,)), ("naf", ("not_val", ('i', 'j', v)))]
            ))

        # Rule index
        self.exact_rule_index = {}
        self.pred_rule_index = {}

        for rule in kb.rules:
            self.exact_rule_index.setdefault(rule.head, []).append(rule)
            self.pred_rule_index.setdefault(rule.head[0], []).append(rule)

        self._rebuild_fact_index(kb)
        self._rebuild_val_rule_index(kb)
        self.kb_version = 1

        # Validate givens
        for r in range(self.n):
            for c in range(self.n):
                v = self.grid[r][c]
                if v != 0:
                    if any(self.fol_bc_ask(kb, ("not_val", (r, c, v)))):
                        return None

        if self._backtrack(kb, step_callback):
            return self.grid
        return None

    def query(self, kb, goal: Tuple) -> List[Dict]:
        return list(self.fol_bc_ask(kb, goal))

    # ==========================================
    # BC ENGINE
    # ==========================================

    def fol_bc_ask(self, kb, goal):
        yield from self.fol_bc_or(kb, goal, {}, False, set())

    def fol_bc_or(self, kb, goal, theta, in_naf, visited):
        if theta == "failure":
            return

        inst_goal = subst(theta, goal)
        goal_key = (inst_goal, in_naf)

        if goal_key in visited:
            return

        next_visited = visited | {goal_key}

        theta_key = tuple(sorted(theta.items()))
        memo_key = (self.kb_version, goal_key, theta_key)

        if memo_key in self.memo:
            yield from self.memo[memo_key]
            return

        results = []
        pred, args = inst_goal

        # ===== NAF =====
        if pred == "naf":
            inner = args
            can_prove = any(True for _ in self.fol_bc_or(kb, inner, theta, True, next_visited))
            if not can_prove:
                results.append(theta)
                yield theta

        else:
            # ===== FACTS =====
            if pred == "val" and not is_variable(args[0]) and not is_variable(args[1]):
                fact_candidates = self.val_fact_cell_index.get((args[0], args[1]), [])
            else:
                fact_candidates = self.fact_index.get(pred, [])

            for clause in reversed(fact_candidates):
                theta2 = unify(args, clause.head[1], theta)
                if theta2 != "failure":
                    for res in self.fol_bc_and(kb, clause.body, theta2, in_naf, next_visited):
                        results.append(res)
                        yield res

            # ===== RULES =====
            if not (in_naf and pred == "val"):
                if is_ground_expr(args):
                    candidates = self.exact_rule_index.get(inst_goal, [])
                elif pred == "val" and not is_variable(args[0]) and not is_variable(args[1]):
                    candidates = self.val_rule_cell_index.get((args[0], args[1]), []) + self.val_rule_generic
                else:
                    candidates = self.pred_rule_index.get(pred, [])

                for rule in candidates:
                    theta2 = unify(args, rule.head[1], theta)
                    if theta2 != "failure":
                        for res in self.fol_bc_and(kb, rule.body, theta2, in_naf, next_visited):
                            results.append(res)
                            yield res

        self.memo[memo_key] = results

    def fol_bc_and(self, kb, goals, theta, in_naf, visited):
        if theta == "failure":
            return
        if not goals:
            yield theta
            return

        first = subst(theta, goals[0])
        rest = goals[1:]

        for theta2 in self.fol_bc_or(kb, first, theta, in_naf, visited):
            yield from self.fol_bc_and(kb, rest, theta2, in_naf, visited)

    # ==========================================
    # BACKTRACK
    # ==========================================

    def _select_cell_mrv(self, kb):
        best_cell = None
        best_values = None

        for i in range(self.n):
            for j in range(self.n):
                if self.grid[i][j] != 0:
                    continue

                values = []
                seen = set()
                for theta in self.query(kb, ("val", (i, j, 'v'))):
                    v = theta.get('v')
                    if v is None or v in seen:
                        continue
                    seen.add(v)
                    values.append(v)

                if not values:
                    return (i, j, [])

                if best_values is None or len(values) < len(best_values):
                    best_cell = (i, j)
                    best_values = values
                    if len(best_values) == 1:
                        return best_cell[0], best_cell[1], best_values

        if best_cell is None:
            return None
        return best_cell[0], best_cell[1], best_values

    def _backtrack(self, kb, step_callback=None):
        if self.found_solution:
            return True

        self.increment_nodes()
        if self.has_exceeded_max_nodes():
            return False

        mrv_pick = self._select_cell_mrv(kb)
        if mrv_pick is None:
            self.found_solution = True
            return True
        r, c, candidates = mrv_pick
        if not candidates:
            return False

        for v in candidates:

            self.grid[r][c] = v
            if step_callback:
                step_callback(r, c, v)

            fact = HornClause(head=("val", (r, c, v)))
            kb.facts.append(fact)
            self._index_add(fact)
            self.kb_version += 1

            if self._backtrack(kb, step_callback):
                return True

            kb.facts.pop()
            self._index_remove(fact)
            self.kb_version += 1

            self.grid[r][c] = 0
            if step_callback:
                step_callback(r, c, 0)

        return False