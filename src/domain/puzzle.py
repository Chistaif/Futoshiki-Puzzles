from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple
import copy


@dataclass(frozen=True)
class PuzzleCase:
    name: str
    path: Path
    n: int
    grid: List[List[int]]
    horizontal: List[List[int]]
    vertical: List[List[int]]


class Puzzle:
    """Mutable puzzle model used by search algorithms."""

    def __init__(self, case: PuzzleCase):
        self.n = case.n
        self.grid = copy.deepcopy(case.grid)
        self.horizontal = case.horizontal
        self.vertical = case.vertical

    def copy(self) -> "Puzzle":
        cloned = Puzzle.__new__(Puzzle)
        cloned.n = self.n
        cloned.grid = copy.deepcopy(self.grid)
        cloned.horizontal = self.horizontal
        cloned.vertical = self.vertical
        return cloned

    def is_complete(self) -> bool:
        return all(value != 0 for row in self.grid for value in row)

    def get_empty_cells(self) -> List[Tuple[int, int]]:
        cells: List[Tuple[int, int]] = []
        for i in range(self.n):
            for j in range(self.n):
                if self.grid[i][j] == 0:
                    cells.append((i, j))
        return cells

    def is_valid(self, row: int, col: int, val: int) -> bool:
        for c in range(self.n):
            if self.grid[row][c] == val:
                return False

        for r in range(self.n):
            if self.grid[r][col] == val:
                return False

        if col < self.n - 1:
            sign = self.horizontal[row][col]
            right = self.grid[row][col + 1]
            if sign != 0 and right != 0:
                if sign == 1 and not (val < right):
                    return False
                if sign == -1 and not (val > right):
                    return False

        if col > 0:
            sign = self.horizontal[row][col - 1]
            left = self.grid[row][col - 1]
            if sign != 0 and left != 0:
                if sign == 1 and not (left < val):
                    return False
                if sign == -1 and not (left > val):
                    return False

        if row < self.n - 1:
            sign = self.vertical[row][col]
            bottom = self.grid[row + 1][col]
            if sign != 0 and bottom != 0:
                if sign == 1 and not (val < bottom):
                    return False
                if sign == -1 and not (val > bottom):
                    return False

        if row > 0:
            sign = self.vertical[row - 1][col]
            top = self.grid[row - 1][col]
            if sign != 0 and top != 0:
                if sign == 1 and not (top < val):
                    return False
                if sign == -1 and not (top > val):
                    return False

        return True


def to_tuple(case: PuzzleCase) -> Tuple[int, List[List[int]], List[List[int]], List[List[int]]]:
    return case.n, case.grid, case.horizontal, case.vertical


def from_tuple(
    file_name: str,
    n: int,
    grid: List[List[int]],
    horizontal: List[List[int]],
    vertical: List[List[int]],
) -> PuzzleCase:
    return PuzzleCase(name=file_name, path=Path(file_name), n=n, grid=grid, horizontal=horizontal, vertical=vertical)

