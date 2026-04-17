"""BoardModel for Futoshiki board state and rule validation.

This module contains pure game-state logic (data + constraint checks) and does
not depend on pygame.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from src.domain.puzzle import PuzzleCase


class BoardModel:
    """Store board values and validate Futoshiki constraints."""

    def __init__(self, n: int) -> None:
        self.n = n
        self.values: List[List[int]] = []
        self.clues: Dict[Tuple[int, int], int] = {}
        self.horizontal_relations: Dict[Tuple[int, int], str] = {}
        self.vertical_relations: Dict[Tuple[int, int], str] = {}
        self.invalid_positions: set[Tuple[int, int]] = set()
        self.initialize_empty(n)

    def initialize_empty(self, n: int) -> None:
        self.n = n
        self.values = [[0 for _ in range(n)] for _ in range(n)]
        self.clues = {}
        self.horizontal_relations = {}
        self.vertical_relations = {}
        self.invalid_positions = set()

    def load_case(self, case: PuzzleCase) -> None:
        self.n = case.n
        self.values = [row[:] for row in case.grid]
        self.clues = {}
        self.horizontal_relations = {}
        self.vertical_relations = {}
        self.invalid_positions = set()

        for row in range(self.n):
            for col in range(self.n):
                value = case.grid[row][col]
                if value != 0:
                    self.clues[(row, col)] = value

        for row in range(self.n):
            for col in range(self.n - 1):
                relation = case.horizontal[row][col]
                if relation == 1:
                    self.horizontal_relations[(row, col)] = "<"
                elif relation == -1:
                    self.horizontal_relations[(row, col)] = ">"

        for row in range(self.n - 1):
            for col in range(self.n):
                relation = case.vertical[row][col]
                if relation == 1:
                    self.vertical_relations[(row, col)] = "^"
                elif relation == -1:
                    self.vertical_relations[(row, col)] = "v"

    def is_clue(self, row: int, col: int) -> bool:
        return (row, col) in self.clues

    def set_value(self, row: int, col: int, value: int) -> bool:
        if not (0 <= row < self.n and 0 <= col < self.n):
            return False

        if value < 0 or value > self.n:
            return False

        if self.is_clue(row, col):
            return False

        self.values[row][col] = value
        return True

    def revalidate_board(self) -> None:
        self.invalid_positions = set()
        self._validate_rows()
        self._validate_cols()
        self._validate_horizontal()
        self._validate_vertical()

    def is_filled(self) -> bool:
        return all(value != 0 for row in self.values for value in row)

    @staticmethod
    def relation_is_satisfied(symbol: str, left_value: int, right_value: int) -> bool:
        if left_value == 0 or right_value == 0:
            return False

        if symbol in ("<", "^"):
            return left_value < right_value

        return left_value > right_value

    def _mark_invalid(self, positions: List[Tuple[int, int]]) -> None:
        for row, col in positions:
            self.invalid_positions.add((row, col))

    def _validate_rows(self) -> None:
        for row in range(self.n):
            seen: Dict[int, List[Tuple[int, int]]] = {}
            for col in range(self.n):
                value = self.values[row][col]
                if value == 0:
                    continue
                if value < 1 or value > self.n:
                    self.invalid_positions.add((row, col))
                seen.setdefault(value, []).append((row, col))

            for positions in seen.values():
                if len(positions) > 1:
                    self._mark_invalid(positions)

    def _validate_cols(self) -> None:
        for col in range(self.n):
            seen: Dict[int, List[Tuple[int, int]]] = {}
            for row in range(self.n):
                value = self.values[row][col]
                if value == 0:
                    continue
                seen.setdefault(value, []).append((row, col))

            for positions in seen.values():
                if len(positions) > 1:
                    self._mark_invalid(positions)

    def _validate_horizontal(self) -> None:
        for (row, col), symbol in self.horizontal_relations.items():
            left = self.values[row][col]
            right = self.values[row][col + 1]

            if symbol == "<":
                if left == self.n:
                    self.invalid_positions.add((row, col))
                if right == 1:
                    self.invalid_positions.add((row, col + 1))
                if left != 0 and right != 0 and not (left < right):
                    self._mark_invalid([(row, col), (row, col + 1)])
            else:
                if left == 1:
                    self.invalid_positions.add((row, col))
                if right == self.n:
                    self.invalid_positions.add((row, col + 1))
                if left != 0 and right != 0 and not (left > right):
                    self._mark_invalid([(row, col), (row, col + 1)])

    def _validate_vertical(self) -> None:
        for (row, col), symbol in self.vertical_relations.items():
            top = self.values[row][col]
            bottom = self.values[row + 1][col]

            if symbol == "^":
                if top == self.n:
                    self.invalid_positions.add((row, col))
                if bottom == 1:
                    self.invalid_positions.add((row + 1, col))
                if top != 0 and bottom != 0 and not (top < bottom):
                    self._mark_invalid([(row, col), (row + 1, col)])
            else:
                if top == 1:
                    self.invalid_positions.add((row, col))
                if bottom == self.n:
                    self.invalid_positions.add((row + 1, col))
                if top != 0 and bottom != 0 and not (top > bottom):
                    self._mark_invalid([(row, col), (row + 1, col)])

