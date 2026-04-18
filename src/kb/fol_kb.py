from src.domain.puzzle import PuzzleCase

class FOLKB:
    """Tự động tạo CNF cho KB."""

    def __init__(self, puzzle: PuzzleCase):
        """Khởi tạo ban đầu. List clause sẽ lưu toàn bộ mệnh đề đã tạo."""
        self.n = puzzle.n
        self.grid = puzzle.grid
        self.horizontal = puzzle.horizontal
        self.vertical = puzzle.vertical
        self.clauses = []

    def var(self, i: int, j: int, v: int) -> int:
        """
        Ánh xạ (i, j, v) thành số nguyên ID, là số thứ tự của mệnh đề trong clause.
        i, j = [0, n-1]
        v = [1, n]
        => ID = [1, N^3]
        Công thức: ID = i*N^2 + j*N + v
        """
        return i*self.n*self.n + j*self.n + v

    def cell_at_least_one(self):
        """A1: Mỗi ô chứa ít nhất một giá trị."""
        for i in range(self.n):
            for j in range(self.n):
                clause = []
                for v in range(1, self.n + 1):
                    clause.append(self.var(i, j, v))
                self.clauses.append(clause)

    def cell_at_most_one(self):
        """A2: Mỗi ô có nhiều nhất một giá trị."""
        for i in range(self.n):
            for j in range(self.n):
                for a in range(1, self.n + 1):
                    for b in range(a + 1, self.n + 1):
                        self.clauses.append([-self.var(i, j, a), -self.var(i, j, b)])

    def row_constraints(self):
        """A3: Các ô trên cùng một hàng không được cùng giá trị."""
        for i in range(self.n):
            for v in range(1, self.n + 1):
                for j1 in range(self.n):
                    for j2 in range(j1 + 1, self.n):
                        self.clauses.append([-self.var(i, j1, v), -self.var(i, j2, v)])
    
    def col_constraints(self):
        """A4: Các ô trên cùng một cột không được cùng giá trị."""
        for j in range(self.n):
            for v in range(1, self.n + 1):
                for i1 in range(self.n):
                    for i2 in range(i1 + 1, self.n):
                        self.clauses.append([-self.var(i1, j, v), -self.var(i2, j, v)])


    def horizontal_constraints(self):
        """
        A5: (i, j, v1) < (i, j + 1, v2)
        A6: (i, j, v1) > (i, j + 1, v2)
        """
        for i in range(self.n):
            for j in range(self.n - 1):
                sign = self.horizontal[i][j]

                if sign == 0: continue # Bỏ qua nếu không có ràng buộc
                
                for a in range(1, self.n + 1):
                    for b in range(1, self.n + 1):
                        # Dấu <
                        if sign == 1 and not (a < b):
                            self.clauses.append([-self.var(i, j, a), -self.var(i, j + 1, b)])
                        # Dấu >
                        elif sign == -1 and not (a > b):
                            self.clauses.append([-self.var(i, j, a), -self.var(i, j + 1, b)])
    
    def vertical_constraints(self):
        """
        A7: (i, j, v1) < (i + 1, j, v2)
        A8: (i, j, v1) > (i + 1, j, v2)
        """
        for i in range(self.n - 1):
            for j in range(self.n):
                sign = self.vertical[i][j]

                if sign == 0: continue # Bỏ qua nếu không có ràng buộc
                
                for a in range(1, self.n + 1):
                    for b in range(1, self.n + 1):
                        # Dấu ^
                        if sign == 1 and not (a < b):
                            self.clauses.append([-self.var(i, j, a), -self.var(i + 1, j, b)])
                        # Dấu v
                        elif sign == -1 and not (a > b):
                            self.clauses.append([-self.var(i, j, a), -self.var(i + 1, j, b)])
    
    def given_constraints(self):
        """A9: Ô được gán giá trị cho sẵn thì cố định lại."""
        for i in range(self.n):
            for j in range(self.n):
                if self.grid[i][j] != 0:
                    v = self.grid[i][j]
                    self.clauses.append([self.var(i, j, v)])

    """A10: đã được encode ngầm => không thể có value ngoài [1..N]."""
    """A11: đã có not(a < b) thay vì less."""

    def build_KB(self):
        self.clauses = []
        self.cell_at_least_one()
        self.cell_at_most_one()
        self.row_constraints()
        self.col_constraints()
        self.given_constraints()
        self.horizontal_constraints()
        self.vertical_constraints()

        return self.clauses

