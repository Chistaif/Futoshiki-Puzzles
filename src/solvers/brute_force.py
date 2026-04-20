from src.solvers.solver import Solver
from src.domain.puzzle import PuzzleCase
import itertools
import copy
from typing import Optional

class BruteForceSolver(Solver):
    """Giải bài toán bằng thuật toán Brute Force THUẦN

    Ý tưởng:
    - Lấy tất cả ô trống
    - Sinh mọi cách gán value
    - Fill đầy puzzle
    - Check valid sau cùng
    """
    def __init__(self, puzzle: PuzzleCase):
        super().__init__(name = "BruteForceSolver")
        self.n = puzzle.n
        self.grid = copy.deepcopy(puzzle.grid)
        self.horizontal = puzzle.horizontal
        self.vertical = puzzle.vertical

    def is_valid(self) -> bool:
        """Check toàn bộ bảng sau khi đã fill xong. """

        n = self.n

        # 1. check row
        for i in range(n):
            if len(set(self.grid[i])) != n:
                return False 
        
        # 2. check column
        for j in range(n):
            col = [self.grid[i][j] for i in range(n)]
            if len(set(col)) != n:
                return False
            
        # 3. check horizontal constraints
        for i in range(n):
            for j in range(n - 1):
                sign = self.horizontal[i][j]
                if sign != 0:
                    if sign == 1 and not(self.grid[i][j] < self.grid[i][j + 1]):
                        return False
                    if sign == -1 and not(self.grid[i][j] > self.grid[i][j + 1]):
                        return False
                    
        # 4. check vertical constraints
        for i in range(n - 1):
            for j in range(n):
                sign = self.vertical[i][j]
                if sign != 0:
                    if sign == 1 and not(self.grid[i][j] < self.grid[i + 1][j]):
                        return False
                    if sign == -1 and not(self.grid[i][j] > self.grid[i + 1][j]):
                        return False
                    
        return True
    
    def solve(self, step_callback = None) -> Optional[list]:
        """Brute Force Solver"""

        #find empty cell
        empty_cells = [
            (i, j)
            for i in range(self.n)
            for j in range(self.n)
            if self.grid[i][j] == 0
        ]

        values = list(range(1, self.n + 1))

        #luu lai grid cho phan sau
        original_grid = copy.deepcopy(self.grid)

        #thử hết khả năng
        for assignment in itertools.product(values, repeat=len(empty_cells)):
            self.increment_nodes()

            #copy lại grid sau mỗi lần thử
            temp_grid = copy.deepcopy(original_grid)

            #fill toan bo
            for (i, j), val in zip(empty_cells, assignment):
                temp_grid[i][j] = val

            #assign tạm vào self de reuse check
            self.grid = temp_grid

            #Final -> check
            if self.is_valid():
                return self.grid
        
        return None