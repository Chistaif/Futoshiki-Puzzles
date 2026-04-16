import copy
from src.domain.puzzle import PuzzleCase
from typing import Callable, Optional


StepCallback = Callable[[int, int, int], None]


class Backtracking:
    """Giáº£i bÃ i toÃ¡n Futoshiki báº±ng thuáº­t toÃ¡n quay lui (Backtracking).

    Ã tÆ°á»Ÿng chÃ­nh:
    - Duyá»‡t tá»«ng Ã´ trá»‘ng trÃªn báº£ng
    - Thá»­ gÃ¡n cÃ¡c giÃ¡ trá»‹ tá»« 1 â†’ n
    - Kiá»ƒm tra há»£p lá»‡ (row, column, inequality)
    - Náº¿u há»£p lá»‡ thÃ¬ tiáº¿p tá»¥c Ä‘á»‡ quy
    - Náº¿u khÃ´ng thÃ¬ quay lui (backtrack)
    """

    def __init__(self, puzzle: PuzzleCase):
        """Khá»Ÿi táº¡o solver tá»« má»™t PuzzleCase.

        - Sao chÃ©p grid Ä‘á»ƒ trÃ¡nh lÃ m thay Ä‘á»•i dá»¯ liá»‡u gá»‘c
        - LÆ°u láº¡i cÃ¡c rÃ ng buá»™c ngang vÃ  dá»c
        """
        self.n = puzzle.n
        self.grid = copy.deepcopy(puzzle.grid)
        self.horizontal = puzzle.horizontal
        self.vertical = puzzle.vertical

    def is_valid(self, row: int, col: int, val: int) -> bool:
        """Kiá»ƒm tra xem cÃ³ thá»ƒ Ä‘áº·t giÃ¡ trá»‹ val vÃ o Ã´ (row, col) hay khÃ´ng.

        CÃ¡c Ä‘iá»u kiá»‡n cáº§n thá»a:
        1. KhÃ´ng trÃ¹ng trong hÃ ng
        2. KhÃ´ng trÃ¹ng trong cá»™t
        3. Thá»a rÃ ng buá»™c ngang (< hoáº·c >)
        4. Thá»a rÃ ng buá»™c dá»c (< hoáº·c >)
        """

        # ========================
        # 1. Kiá»ƒm tra hÃ ng (row)
        # ========================
        for c in range(self.n):
            if self.grid[row][c] == val:
                return False

        # ========================
        # 2. Kiá»ƒm tra cá»™t (column)
        # ========================
        for r in range(self.n):
            if self.grid[r][col] == val:
                return False

        # ========================
        # 3. Kiá»ƒm tra rÃ ng buá»™c ngang
        # ========================

        # Ã” bÃªn pháº£i (row, col+1)
        if col < self.n - 1:
            sign = self.horizontal[row][col]

            # Chá»‰ kiá»ƒm tra khi cÃ³ rÃ ng buá»™c vÃ  Ã´ bÃªn pháº£i Ä‘Ã£ cÃ³ giÃ¡ trá»‹
            if sign != 0 and self.grid[row][col + 1] != 0:
                # sign == 1: Ã´ trÃ¡i < Ã´ pháº£i
                if sign == 1 and not (val < self.grid[row][col + 1]):
                    return False
                # sign == -1: Ã´ trÃ¡i > Ã´ pháº£i
                if sign == -1 and not (val > self.grid[row][col + 1]):
                    return False

        # Ã” bÃªn trÃ¡i (row, col-1)
        if col > 0:
            sign = self.horizontal[row][col - 1]

            if sign != 0 and self.grid[row][col - 1] != 0:
                # sign == 1: Ã´ trÃ¡i < Ã´ pháº£i
                if sign == 1 and not (self.grid[row][col - 1] < val):
                    return False
                # sign == -1: Ã´ trÃ¡i > Ã´ pháº£i
                if sign == -1 and not (self.grid[row][col - 1] > val):
                    return False

        # ========================
        # 4. Kiá»ƒm tra rÃ ng buá»™c dá»c
        # ========================

        # Ã” phÃ­a dÆ°á»›i (row+1, col)
        if row < self.n - 1:
            sign = self.vertical[row][col]

            if sign != 0 and self.grid[row + 1][col] != 0:
                # sign == 1: Ã´ trÃªn < Ã´ dÆ°á»›i
                if sign == 1 and not (val < self.grid[row + 1][col]):
                    return False
                # sign == -1: Ã´ trÃªn > Ã´ dÆ°á»›i
                if sign == -1 and not (val > self.grid[row + 1][col]):
                    return False

        # Ã” phÃ­a trÃªn (row-1, col)
        if row > 0:
            sign = self.vertical[row - 1][col]

            if sign != 0 and self.grid[row - 1][col] != 0:
                # sign == 1: Ã´ trÃªn < Ã´ dÆ°á»›i
                if sign == 1 and not (self.grid[row - 1][col] < val):
                    return False
                # sign == -1: Ã´ trÃªn > Ã´ dÆ°á»›i
                if sign == -1 and not (self.grid[row - 1][col] > val):
                    return False

        return True

    def find_empty(self):
        """TÃ¬m má»™t Ã´ trá»‘ng (giÃ¡ trá»‹ = 0) trÃªn báº£ng.

        Tráº£ vá»:
        - (row, col) náº¿u cÃ²n Ã´ trá»‘ng
        - None náº¿u báº£ng Ä‘Ã£ Ä‘áº§y
        """
        for i in range(self.n):
            for j in range(self.n):
                if self.grid[i][j] == 0:
                    return i, j
        return None

    def backtrack(self, step_callback: Optional[StepCallback] = None) -> bool:
        """Thuáº­t toÃ¡n quay lui chÃ­nh.

        Quy trÃ¬nh:
        - TÃ¬m Ã´ trá»‘ng
        - Thá»­ táº¥t cáº£ giÃ¡ trá»‹ há»£p lá»‡
        - Náº¿u Ä‘áº·t Ä‘Æ°á»£c thÃ¬ gá»i Ä‘á»‡ quy
        - Náº¿u tháº¥t báº¡i thÃ¬ quay lui
        """

        empty = self.find_empty()

        # Náº¿u khÃ´ng cÃ²n Ã´ trá»‘ng â†’ Ä‘Ã£ giáº£i xong
        if not empty:
            return True

        i, j = empty

        # Thá»­ cÃ¡c giÃ¡ trá»‹ tá»« 1 â†’ n
        for val in range(1, self.n + 1):
            if self.is_valid(i, j, val):
                # GÃ¡n thá»­
                self.grid[i][j] = val
                if step_callback is not None:
                    step_callback(i, j, val)

                # Äá»‡ quy
                if self.backtrack(step_callback):
                    return True

                # Quay lui
                self.grid[i][j] = 0
                if step_callback is not None:
                    step_callback(i, j, 0)

        return False

    def solve(self, step_callback: Optional[StepCallback] = None):
        """HÃ m public Ä‘á»ƒ giáº£i puzzle.

        Tráº£ vá»:
        - grid Ä‘Ã£ giáº£i náº¿u cÃ³ nghiá»‡m
        - None náº¿u khÃ´ng cÃ³ nghiá»‡m
        """
        if self.backtrack(step_callback):
            return self.grid
        return None
