import copy
from src.domain.puzzle import PuzzleCase
from src.solvers.solver import MAX_NODES_BACKTRACKING, Solver
from typing import Callable, Optional
from pathlib import Path


StepCallback = Callable[[int, int, int], None]


class Backtracking(Solver):
    """Giải bài toán Futoshiki bằng thuật toán quay lui (Backtracking).

    Ý tưởng chính:
    - Duyệt từng ô trống trên bảng.
    - Thử gán các giá trị từ 1 -> n.
    - Kiểm tra hợp lệ (row, column, inequality).
    - Nếu hợp lệ thì tiếp tục đệ quy.
    - Nếu không thì quay lui (backtrack).
    """

    def __init__(self, puzzle: PuzzleCase):
        """Khởi tạo solver từ một PuzzleCase.

        - Sao chép grid để tránh làm thay đổi dữ liệu gốc.
        - Lưu lại các ràng buộc ngang và dọc.
        """
        super().__init__(name="Backtracking")
        self.max_nodes = MAX_NODES_BACKTRACKING
        self.n = puzzle.n
        self.grid = copy.deepcopy(puzzle.grid)
        self.horizontal = puzzle.horizontal
        self.vertical = puzzle.vertical

    def is_valid(self, row: int, col: int, val: int) -> bool:
        """Kiểm tra xem có thể đặt giá trị val vào ô (row, col) hay không.

        Các điều kiện cần thỏa:
        1. Không trùng trong hàng.
        2. Không trùng trong cột.
        3. Thỏa ràng buộc ngang (< hoặc >).
        4. Thỏa ràng buộc dọc (< hoặc >).
        """

        # ========================
        # 1. Kiểm tra hàng (row)
        # ========================
        for c in range(self.n):
            if self.grid[row][c] == val:
                return False

        # ========================
        # 2. Kiểm tra cột (column)
        # ========================
        for r in range(self.n):
            if self.grid[r][col] == val:
                return False

        # ========================
        # 3. Kiểm tra ràng buộc ngang
        # ========================

        # Ô bên phải (row, col+1)
        if col < self.n - 1:
            sign = self.horizontal[row][col]

            # Chỉ kiểm tra khi có ràng buộc và ô bên phải đã có giá trị
            if sign != 0 and self.grid[row][col + 1] != 0:
                # sign == 1: ô trái < ô phải
                if sign == 1 and not (val < self.grid[row][col + 1]):
                    return False
                # sign == -1: ô trái > ô phải
                if sign == -1 and not (val > self.grid[row][col + 1]):
                    return False

        # Ô bên trái (row, col-1)
        if col > 0:
            sign = self.horizontal[row][col - 1]

            if sign != 0 and self.grid[row][col - 1] != 0:
                # sign == 1: ô trái < ô phải
                if sign == 1 and not (self.grid[row][col - 1] < val):
                    return False
                # sign == -1: ô trái > ô phải
                if sign == -1 and not (self.grid[row][col - 1] > val):
                    return False

        # ========================
        # 4. Kiểm tra ràng buộc dọc
        # ========================

        # Ô phía dưới (row+1, col)
        if row < self.n - 1:
            sign = self.vertical[row][col]

            if sign != 0 and self.grid[row + 1][col] != 0:
                # sign == 1: ô trên < ô dưới
                if sign == 1 and not (val < self.grid[row + 1][col]):
                    return False
                # sign == -1: ô trên > ô dưới
                if sign == -1 and not (val > self.grid[row + 1][col]):
                    return False

        # Ô phía trên (row-1, col)
        if row > 0:
            sign = self.vertical[row - 1][col]

            if sign != 0 and self.grid[row - 1][col] != 0:
                # sign == 1: ô trên < ô dưới
                if sign == 1 and not (self.grid[row - 1][col] < val):
                    return False
                # sign == -1: ô trên > ô dưới
                if sign == -1 and not (self.grid[row - 1][col] > val):
                    return False

        return True

    def find_empty(self):
        """Tìm một ô trống (giá trị = 0) trên bảng.

        Trả về:
        - (row, col) nếu còn ô trống.
        - None nếu bảng đã đầy.
        """
        for i in range(self.n):
            for j in range(self.n):
                if self.grid[i][j] == 0:
                    return i, j
        return None

    def backtrack(self, step_callback: Optional[StepCallback] = None) -> bool:
        """Thuật toán quay lui chính.

        Quy trình:
        - Tìm ô trống.
        - Thử tất cả giá trị hợp lệ.
        - Nếu đặt được thì gọi đệ quy.
        - Nếu thất bại thì quay lui.
        """

        self.increment_nodes()
        if self.has_exceeded_max_nodes():
            return False
        empty = self.find_empty()

        # Nếu không còn ô trống -> đã giải xong
        if not empty:
            return True

        i, j = empty

        # Thử các giá trị từ 1 -> n
        for val in range(1, self.n + 1):
            if self.is_valid(i, j, val):
                # Gán thử
                self.grid[i][j] = val
                if step_callback is not None:
                    step_callback(i, j, val)

                # Đệ quy
                if self.backtrack(step_callback):
                    return True

                # Quay lui
                self.grid[i][j] = 0
                if step_callback is not None:
                    step_callback(i, j, 0)

        return False
    
    def write_output(self, filename: str, solved: bool = True):
        output_dir = Path("Outputs")
        output_dir.mkdir(exist_ok = True) 

        file_path = output_dir / filename
        with open(filename, "w") as f:
                if not solved:
                    f.write("No solution found.\n")
                    return

                f.write(f"Solution ({self.n}x{self.n}):\n")
                for row in self.grid:
                    f.write(" ".join(map(str, row)) + "\n")

    def solve(self, step_callback: Optional[StepCallback] = None, output_file: Optional[str] = None):
        """Hàm public để giải puzzle.

        Trả về:
        - grid đã giải nếu có nghiệm.
        - None nếu không có nghiệm.
        """
        if self.backtrack(step_callback):
            if output_file:
                self.write_output(output_file)
            return self.grid
        
        if output_file:
            self.write_output(output_file, solved = False)
        return None
