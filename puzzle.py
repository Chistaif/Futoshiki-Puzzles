class FutoshikiPuzzle:
    def __init__(self,data):
        self.N = data["N"]
        self.puzzle = data["puzzle"]
        self.horizontal = data["horizontal"]
        self.vertical = data["vertical"]

    #hàm check valid
    def is_valid(self, row, col, val):
        #mục đích: kiểm tra xem trong row/column đã có số val hay chưa nếu có rồi => False

        #check row
        for c in range(self.N):
            if c != col and self.puzzle[row][c] == val:
                return False
            
        #check column
        for r in range(self.N):
            if r != row and self.puzzle[r][col] == val:
                return False
            
        #check ngang - horizontal: 0 = no constraint, 1 = left < right, -1 = left > right
        #check trái
        if col > 0:
            constraint = self.horizontal[row][col - 1]
            left = self.puzzle[row][col - 1]

            if left != 0:
                if constraint == 1 and not(left < val):
                    return False
                if constraint == -1 and not(left > val):
                    return False
            
        #check phải
        if col < self.N - 1:
            constraint = self.horizontal[row][col]
            right = self.puzzle[row][col + 1]

            if right != 0:
                if constraint == 1 and not(val < right):
                    return False
                if constraint == -1 and not(val > right):
                    return False
            
        #check dọc - vertical: 0 = no, 1 = top < bottom, -1 = top > bottom
        #check trên
        if row > 0:
            constraint = self.vertical[row - 1][col]
            top = self.puzzle[row - 1][col]

            if top != 0:
                if constraint == 1 and not(top < val):
                    return False
                if constraint == -1 and not(top > val):
                    return False
                
        #check dưới
        if row < self.N - 1:
            constraint = self.vertical[row][col]
            bottom = self.puzzle[row + 1][col]

            if bottom != 0:
                if constraint == 1 and not(val < bottom):
                    return False
                if constraint == -1 and not(val > bottom):
                    return False
                
        return True
                
    #find empty square
    def find_empty(self):
        for i in range(self.N):
            for j in range(self.N):
                if self.puzzle[i][j] == 0:
                    return i, j
        return None
    
    #GOAL
    def is_goal(self):
        return self.find_empty() is None