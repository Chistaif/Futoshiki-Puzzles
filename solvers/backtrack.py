import copy

class Backtracking:
    def __init__(self, puzzle):
        self.n = puzzle.n
        self.grid = copy.deepcopy(puzzle.grid)
        self.horizontal = puzzle.horizontal
        self.vertical = puzzle.vertical

    def is_valid(self, row, col, val):
        #check row
        for c in range(self.n):
            if self.grid[row][c] == val and c != col:
                return False
            
        #check column
        for r in range(self.n):
            if self.grid[r][col] == val and r != row:
                return False
            
        #horizontal - right
        if col < self.n - 1 and self.horizontal[row][col] not in (None, ""):
            sign = self.horizontal[row][col]

            if self.grid[row][col + 1] != 0:
                if sign == "<" and not(val < self.grid[row][col + 1]):
                    return False
                if sign == ">" and not(val > self.grid[row][col + 1]):
                    return False
                
        #horizontal - left
        if col > 0 and self.horizontal[row][col - 1] not in (None, ""):
            sign = self.horizontal[row][col - 1]

            if self.grid[row][col - 1] != 0:
                if sign == "<" and not(self.grid[row][col - 1] < val):
                    return False
                if sign == ">" and not(self.grid[row][col - 1] > val):
                    return False
        
        #vertical - down
        if row < self.n - 1 and self.vertical[row][col] not in (None, ""):
            sign = self.vertical[row][col]

            if self.grid[row + 1][col] != 0:
                if sign == "v" and not(val < self.grid[row + 1][col]):
                    return False
                if sign == "^" and not(val > self.grid[row + 1][col]):
                    return False
        
        #vertical - up
        if row > 0 and self.vertical[row - 1][col] not in (None, ""):
            sign = self.vertical[row - 1][col]

            if self.grid[row - 1][col] != 0:
                if sign == "v" and not(self.grid[row - 1][col] < val):
                    return False
                if sign == "^" and not(self.grid[row - 1][col] > val):
                    return False
                
        return True
    

    def find_empty(self):
        for i in range(self.n):
            for j in range(self.n):
                if self.grid[i][j] == 0:
                    return i, j
        return None
    
    def backtrack(self):
        empty = self.find_empty()
        if not empty:
            return True

        i, j = empty

        for val in range(1, self.n + 1):
            if self.is_valid(i, j, val):
                self.grid[i][j] = val

                if self.backtrack():
                    return True

                self.grid[i][j] = 0

        return False 
    
    def solve(self):
        if self.backtrack():
            return self.grid
        return None