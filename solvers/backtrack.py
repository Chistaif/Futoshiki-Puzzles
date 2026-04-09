class Backtracking:
    def __init__(self, puzzle):
        self.N = puzzle.N
        self.grid = puzzle.puzzle
        self.horizontal = puzzle.horizontal
        self.vertical = puzzle.vertical

    def is_valid(self, row, col, val):
        #check row
        for c in range(self.N):
            if self.grid[row][c] == val:
                return False
            
        #check column
        for r in range(self.N):
            if self.grid[r][col] == val:
                return False
            
        #horizontal - right
        if col < self.N - 1 and self.horizontal[row][col]:
            sign = self.horizontal[row][col]

            if self.grid[row][col + 1] != 0:
                if sign == "<" and not(val < self.grid[row][col + 1]):
                    return False
                if sign == ">" and not(val > self.grid[row][col + 1]):
                    return False
                
        #horizontal - left
        if col > 0 and self.horizontal[row][col - 1]:
            sign = self.horizontal[row][col - 1]

            if self.grid[row][col - 1] != 0:
                if sign == "<" and not(self.grid[row][col - 1] < val):
                    return False
                if sign == ">" and not(self.grid[row][col - 1] > val):
                    return False
        
        #vertical - down
        if row < self.N - 1 and self.vertical[row][col]:
            sign = self.vertical[row][col]

            if self.grid[row + 1][col] != 0:
                if sign == "v" and not(val < self.grid[row + 1][col]):
                    return False
                if sign == "^" and not(val > self.grid[row + 1][col]):
                    return False
        
        #vertical - up
        if row > 0 and self.vertical[row - 1][col]:
            sign = self.vertical[row - 1][col]

            if self.grid[row - 1][col] != 0:
                if sign == "v" and not(self.grid[row - 1][col] < val):
                    return False
                if sign == "^" and not(self.grid[row - 1][col] > val):
                    return False
                
        return True
    
    def backtrack(self):
        for i in range(self.N):
            for j in range(self.N):
                if self.grid[i][j] == 0:  
                    for val in range(1, self.N + 1):
                        if self.is_valid(i, j, val):
                            self.grid[i][j] = val

                            if self.backtrack():
                                return True

                            self.grid[i][j] = 0  

                    return False  

        return True  
    
    def solve(self):
        if self.backtrack():
            return self.grid
        return None