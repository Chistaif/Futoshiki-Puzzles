class FOLKB:
    def __init__(self, puzzle):
        self.n = puzzle.n
        self.grid = puzzle.grid
        self.horizontal = puzzle.horizontal
        self.vertical = puzzle.vertical
        self.clauses = []

    #hàm tạo biến 
    def var(self, i, j ,v):
        return f"X{i}{j}{v}"

    #constraint 1 - mỗi ô chỉ có 1 value
    def cell_at_least_one(self):
        for i in range(self.n):
            for j in range(self.n):
                clause = []
                for v in range(1, self.n + 1):
                    clause.append(self.var(i, j, v))
                self.clauses.append(clause)

    #constraint 2 - không có 2 giá trị cùng 1 lúc 
    #có dấu trừ phía trước nghĩa là "-X123" là NOT X123 nếu forward và backward không động bộ thì thiết lập lại
    #tạm thời thống nhất dấu "-" là NOT 
    def cell_at_most_one(self):
        for i in range(self.n):
            for j in range(self.n):
                for a in range(1, self.n + 1):
                    for b in range(a + 1, self.n + 1):
                        self.clauses.append([
                            f"-{self.var(i, j, a)}",
                            f"-{self.var(i, j, b)}"
                        ])

    #constraint row
    def row_constraints(self):
        for i in range(self.n):
            for v in range(1, self.n + 1):
                for j1 in range(self.n):
                    for j2 in range(j1 + 1, self.n):
                        self.clauses.append([
                            f"-{self.var(i, j1, v)}",
                            f"-{self.var(i, j2, v)}"
                        ])


    #constraint column
    def col_constraints(self):
        for j in range(self.n):
            for v in range(1, self.n + 1):
                for i1 in range(self.n):
                    for i2 in range(i1 + 1, self.n):
                        self.clauses.append([
                            f"-{self.var(i1, j ,v)}",
                            f"-{self.var(i2, j, v)}"
                        ])

    #value constraint
    def given_constraints(self):
        for i in range(self.n):
            for j in range(self.n):
                if self.grid[i][j] != 0:
                    v = self.grid[i][j]
                    self.clauses.append([self.var(i, j, v)])

    #horizontal constraint
    def horizontal_constraints(self):
        for i in range(self.n):
            for j in range(self.n - 1):
                sign = self.horizontal[i][j]

                if sign not in (None, ""):
                    for a in range(1, self.n + 1):
                        for b in range(1, self.n + 1):

                            if sign == "<" and not (a < b):
                                self.clauses.append([
                                    f"-{self.var(i, j, a)}",
                                    f"-{self.var(i, j + 1, b)}"
                                ])

                            if sign == ">" and not (a > b):
                                self.clauses.append([
                                    f"-{self.var(i, j, a)}",
                                    f"-{self.var(i, j + 1, b)}"
                                ])

    #vertical constraint
    def vertical_constraints(self):
        for i in range(self.n - 1):
            for j in range(self.n):
                sign = self.vertical[i][j]

                if sign not in (None, ""):
                    for a in range(1, self.n + 1):
                        for b in range(1, self.n + 1):

                            if sign == "v" and not (a < b):
                                self.clauses.append([
                                    f"-{self.var(i, j, a)}",
                                    f"-{self.var(i + 1, j, b)}"
                                ])

                            if sign == "^" and not (a > b):
                                self.clauses.append([
                                    f"-{self.var(i, j, a)}",
                                    f"-{self.var(i + 1, j, b)}"
                                ])


    #gom KB
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