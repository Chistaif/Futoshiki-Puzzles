"""SAT-based solver for Futoshiki using PySAT.

Module này chuyển bộ mệnh đề CNF từ FOLKB sang SAT solver và giải tự động.
Luồng xử lý chính:
1) Sinh KB ở dạng CNF clauses bằng FOLKB.
2) Đưa toàn bộ clauses vào Glucose3.
3) Nếu SAT, giải mã model -> lưới N x N hoàn chỉnh.
4) Nếu UNSAT, trả về None.
"""

from __future__ import annotations

from typing import Callable, List, Optional, Sequence

from src.domain.puzzle import PuzzleCase
from src.kb.fol_kb import FOLKB

try:
    from pysat.solvers import Glucose3
except Exception:  # pragma: no cover - phụ thuộc môi trường cài đặt
    Glucose3 = None


StepCallback = Callable[[int, int, int], None]


class SATSolver:
    """Giải Futoshiki bằng SAT solver (PySAT/Glucose3).

    Class này tuân theo cùng interface solve(step_callback) như các solver khác
    để có thể tích hợp vào GUI manager khi cần.
    """

    def __init__(self, puzzle: PuzzleCase) -> None:
        """Khởi tạo SAT solver từ dữ liệu puzzle.

        Args:
            puzzle: PuzzleCase chứa n, grid và các ràng buộc bất đẳng thức.
        """
        self.puzzle = puzzle
        self.n = puzzle.n
        self.kb_builder = FOLKB(puzzle)

    def solve(self, step_callback: Optional[StepCallback] = None) -> Optional[List[List[int]]]:
        """Giải puzzle bằng SAT và trả về lưới hoàn chỉnh.

        Args:
            step_callback: Callback tùy chọn để stream từng bước gán giá trị.

        Returns:
            Lưới N x N nếu SAT, hoặc None nếu UNSAT/không thể giải.

        Raises:
            RuntimeError: Nếu PySAT chưa được cài hoặc có lỗi nội bộ khi gọi solver.
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
        """Giải mã model SAT thành lưới kết quả N x N.

        Công thức encode trong FOLKB:
            ID = i * N^2 + j * N + v
        với:
            i, j thuộc [0, N-1]
            v thuộc [1, N]
            ID thuộc [1, N^3]

        Ở đây ta decode ngược từ literal dương trong model.
        """
        grid: List[List[int]] = [[0 for _ in range(self.n)] for _ in range(self.n)]

        for literal in model:
            if literal <= 0:
                continue
            if literal > self.n ** 3:
                # Biến ngoài miền Futoshiki, bỏ qua để an toàn.
                continue

            row, col, value = self._decode_variable_id(literal)
            grid[row][col] = value

        # Kiểm tra hậu điều kiện: tất cả ô phải được gán.
        for row in range(self.n):
            for col in range(self.n):
                if grid[row][col] == 0:
                    raise RuntimeError(
                        f"Incomplete SAT model: cell ({row}, {col}) has no value."
                    )

        return grid

    def _decode_variable_id(self, variable_id: int) -> tuple[int, int, int]:
        """Decode biến nguyên -> (row, col, value).

        Biến đổi ngược từ:
            ID = i * N^2 + j * N + v
        """
        zero_based_id = variable_id - 1

        row = zero_based_id // (self.n * self.n)
        remainder = zero_based_id % (self.n * self.n)
        col = remainder // self.n
        value = (remainder % self.n) + 1

        return row, col, value

