"""SAT-based solver for Futoshiki using PySAT.

Module nÃ y chuyá»ƒn bá»™ má»‡nh Ä‘á» CNF tá»« FOLKB sang SAT solver vÃ  giáº£i tá»± Ä‘á»™ng.
Luá»“ng xá»­ lÃ½ chÃ­nh:
1) Sinh KB á»Ÿ dáº¡ng CNF clauses báº±ng FOLKB.
2) ÄÆ°a toÃ n bá»™ clauses vÃ o Glucose3.
3) Náº¿u SAT, giáº£i mÃ£ model -> lÆ°á»›i N x N hoÃ n chá»‰nh.
4) Náº¿u UNSAT, tráº£ vá» None.
"""

from __future__ import annotations

from typing import Callable, List, Optional, Sequence

from src.domain.puzzle import PuzzleCase
from src.kb.fol_kb import FOLKB

try:
    from pysat.solvers import Glucose3
except Exception:  # pragma: no cover - phá»¥ thuá»™c mÃ´i trÆ°á»ng cÃ i Ä‘áº·t
    Glucose3 = None


StepCallback = Callable[[int, int, int], None]


class SATSolver:
    """Giáº£i Futoshiki báº±ng SAT solver (PySAT/Glucose3).

    Class nÃ y tuÃ¢n theo cÃ¹ng interface solve(step_callback) nhÆ° cÃ¡c solver khÃ¡c
    Ä‘á»ƒ cÃ³ thá»ƒ tÃ­ch há»£p vÃ o GUI manager khi cáº§n.
    """

    def __init__(self, puzzle: PuzzleCase) -> None:
        """Khá»Ÿi táº¡o SAT solver tá»« dá»¯ liá»‡u puzzle.

        Args:
            puzzle: PuzzleCase chá»©a n, grid vÃ  cÃ¡c rÃ ng buá»™c báº¥t Ä‘áº³ng thá»©c.
        """
        self.puzzle = puzzle
        self.n = puzzle.n
        self.kb_builder = FOLKB(puzzle)

    def solve(self, step_callback: Optional[StepCallback] = None) -> Optional[List[List[int]]]:
        """Giáº£i puzzle báº±ng SAT vÃ  tráº£ vá» lÆ°á»›i hoÃ n chá»‰nh.

        Args:
            step_callback: Callback tÃ¹y chá»n Ä‘á»ƒ stream tá»«ng bÆ°á»›c gÃ¡n giÃ¡ trá»‹.

        Returns:
            LÆ°á»›i N x N náº¿u SAT, hoáº·c None náº¿u UNSAT/khÃ´ng thá»ƒ giáº£i.

        Raises:
            RuntimeError: Náº¿u PySAT chÆ°a Ä‘Æ°á»£c cÃ i hoáº·c cÃ³ lá»—i ná»™i bá»™ khi gá»i solver.
        """
        if Glucose3 is None:
            raise RuntimeError(
                "PySAT is not available. Please install dependency 'python-sat'."
            )

        try:
            clauses = self.kb_builder.build_KB()
            with Glucose3() as sat_solver:
                sat_solver.append_formula(clauses)

                is_satisfiable = sat_solver.solve()
                if not is_satisfiable:
                    return None

                model = sat_solver.get_model() or []
                solved_grid = self._decode_model_to_grid(model)

                if step_callback is not None:
                    for row in range(self.n):
                        for col in range(self.n):
                            step_callback(row, col, solved_grid[row][col])

                return solved_grid
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(f"SAT solving failed: {exc}") from exc

    def _decode_model_to_grid(self, model: Sequence[int]) -> List[List[int]]:
        """Giáº£i mÃ£ model SAT thÃ nh lÆ°á»›i káº¿t quáº£ N x N.

        CÃ´ng thá»©c encode trong FOLKB:
            ID = i * N^2 + j * N + v
        vá»›i:
            i, j thuá»™c [0, N-1]
            v thuá»™c [1, N]
            ID thuá»™c [1, N^3]

        á»ž Ä‘Ã¢y ta decode ngÆ°á»£c tá»« literal dÆ°Æ¡ng trong model.
        """
        grid: List[List[int]] = [[0 for _ in range(self.n)] for _ in range(self.n)]

        for literal in model:
            if literal <= 0:
                continue
            if literal > self.n ** 3:
                # Biáº¿n ngoÃ i miá»n Futoshiki, bá» qua Ä‘á»ƒ an toÃ n.
                continue

            row, col, value = self._decode_variable_id(literal)
            grid[row][col] = value

        # Kiá»ƒm tra háº­u Ä‘iá»u kiá»‡n: táº¥t cáº£ Ã´ pháº£i Ä‘Æ°á»£c gÃ¡n.
        for row in range(self.n):
            for col in range(self.n):
                if grid[row][col] == 0:
                    raise RuntimeError(
                        f"Incomplete SAT model: cell ({row}, {col}) has no value."
                    )

        return grid

    def _decode_variable_id(self, variable_id: int) -> tuple[int, int, int]:
        """Decode biáº¿n nguyÃªn -> (row, col, value).

        Biáº¿n Ä‘á»•i ngÆ°á»£c tá»«:
            ID = i * N^2 + j * N + v
        """
        zero_based_id = variable_id - 1

        row = zero_based_id // (self.n * self.n)
        remainder = zero_based_id % (self.n * self.n)
        col = remainder // self.n
        value = (remainder % self.n) + 1

        return row, col, value

