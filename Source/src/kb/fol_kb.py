from src.domain.puzzle import PuzzleCase

class FOLKB:
    """Tá»± Ä‘á»™ng táº¡o CNF cho KB"""

    def __init__(self, puzzle: PuzzleCase):
        """Khá»Ÿi táº¡o ban Ä‘áº§u. List clause sáº½ lÆ°u toÃ n bá»™ má»‡nh Ä‘á» Ä‘Ã£ táº¡o"""
        self.n = puzzle.n
        self.grid = puzzle.grid
        self.horizontal = puzzle.horizontal
        self.vertical = puzzle.vertical
        self.clauses = []

    def var(self, i: int, j: int, v: int) -> int:
        """
        Ãnh xáº¡ (i, j, v) thÃ nh sá»‘ int ID, ID lÃ  sá»‘ thá»© tá»± cá»§a má»‡nh Ä‘á» trong clause
        i, j = [0, n-1]
        v = [1, n]
        => ID = [1, N^3]
        CÃ´ng thá»©c: ID = i*N^2 + j*N + v
        """
        return i*self.n*self.n + j*self.n + v

    def cell_at_least_one(self):
        """A1: Má»—i Ã´ chá»©a Ã­t nháº¥t má»™t giÃ¡ trá»‹"""
        for i in range(self.n):
            for j in range(self.n):
                clause = []
                for v in range(1, self.n + 1):
                    clause.append(self.var(i, j, v))
                self.clauses.append(clause)

    def cell_at_most_one(self):
        """A2: Má»—i Ã´ cÃ³ nhiá»u nháº¥t má»™t giÃ¡ trá»‹"""
        for i in range(self.n):
            for j in range(self.n):
                for a in range(1, self.n + 1):
                    for b in range(a + 1, self.n + 1):
                        self.clauses.append([-self.var(i, j, a), -self.var(i, j, b)])

    def row_constraints(self):
        """A3: CÃ¡c Ã´ trÃªn cÃ¹ng má»™t hÃ ng khÃ´ng Ä‘Æ°á»£c cÃ¹ng giÃ¡ trá»‹"""
        for i in range(self.n):
            for v in range(1, self.n + 1):
                for j1 in range(self.n):
                    for j2 in range(j1 + 1, self.n):
                        self.clauses.append([-self.var(i, j1, v), -self.var(i, j2, v)])
    
    def col_constraints(self):
        """A4: CÃ¡c Ã´ trÃªn cÃ¹ng má»™t cá»™t khÃ´ng Ä‘Æ°á»£c cÃ¹ng giÃ¡ trá»‹"""
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

                if sign == 0: continue # Bá» qua náº¿u khÃ´ng cÃ³ rÃ ng buá»™c
                
                for a in range(1, self.n + 1):
                    for b in range(1, self.n + 1):
                        # Dáº¥u <
                        if sign == 1 and not (a < b):
                            self.clauses.append([-self.var(i, j, a), -self.var(i, j + 1, b)])
                        # Dáº¥u >
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

                if sign == 0: continue # Bá» qua náº¿u khÃ´ng cÃ³ rÃ ng buá»™c
                
                for a in range(1, self.n + 1):
                    for b in range(1, self.n + 1):
                        # Dáº¥u ^
                        if sign == 1 and not (a < b):
                            self.clauses.append([-self.var(i, j, a), -self.var(i + 1, j, b)])
                        # Dáº¥u v
                        elif sign == -1 and not (a > b):
                            self.clauses.append([-self.var(i, j, a), -self.var(i + 1, j, b)])
    
    def given_constraints(self):
        """A9: Ã” Ä‘Æ°á»£c gÃ¡n giÃ¡ trá»‹ cho sáºµn thÃ¬ cá»‘ Ä‘á»‹nh láº¡i"""
        for i in range(self.n):
            for j in range(self.n):
                if self.grid[i][j] != 0:
                    v = self.grid[i][j]
                    self.clauses.append([self.var(i, j, v)])

    """A10: Ä‘Ã£ Ä‘Æ°á»£c encode ngáº§m => khÃ´ng thá»ƒ cÃ³ value ngoÃ i [1..N]"""
    """A11: Ä‘Ã£ cÃ³ not(a < b) thay vÃ¬ less"""

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

