"""Main gameplay screen for Futoshiki."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import pygame

from ..components import Button, Cell, Timer
from ..constants import (
    COLOR_BACKGROUND,
    COLOR_BORDER,
    COLOR_CLUE,
    COLOR_ERROR,
    COLOR_MUTED,
    COLOR_PANEL,
    COLOR_SHADOW,
    COLOR_SOLVER,
    COLOR_SUCCESS_SOFT,
    COLOR_TITLE,
    CONTAINER_RADIUS,
    DEFAULT_GRID_SIZE,
    FONT_BUTTON_SIZE,
    FONT_FAMILY,
    FONT_INFO_SIZE,
    GRID_CONFIG,
)
from ..puzzle_loader import PuzzleCase, load_all_input_puzzles
from ..utils import _draw_relation_symbol, _draw_soft_background, _mix

Transition = Optional[Dict[str, Any]]


class GameScreen:
    """Main gameplay scene with live validation and file-based puzzles."""

    def __init__(self, surface_rect: pygame.Rect, n: int = DEFAULT_GRID_SIZE) -> None:
        self.surface_rect = surface_rect

        self._init_fonts()
        self._init_buttons()

        self.n = n
        self.cell_size = 80
        self.cell_gap = 20
        self.relation_size = 18
        self.relation_stroke = 4
        self.container_padding = 24
        self.board_top = 140

        self.values: List[List[int]] = []
        self.clues: Dict[Tuple[int, int], int] = {}
        self.horizontal_relations: Dict[Tuple[int, int], str] = {}
        self.vertical_relations: Dict[Tuple[int, int], str] = {}
        self.cells: List[List[Cell]] = []
        self.selected: Optional[Tuple[int, int]] = None
        self.invalid_positions: set[Tuple[int, int]] = set()

        self.current_case: Optional[PuzzleCase] = None
        self.status_message = ""
        self.board_rect = pygame.Rect(0, 0, 100, 100)

        self.puzzle_cases = load_all_input_puzzles()
        self.puzzles_by_size: Dict[int, List[PuzzleCase]] = {}
        for case in self.puzzle_cases:
            self.puzzles_by_size.setdefault(case.n, []).append(case)

        self.available_sizes: Tuple[int, ...] = tuple(sorted(self.puzzles_by_size.keys()))
        self.case_index_by_size: Dict[int, int] = {size: -1 for size in self.available_sizes}

        preferred = n if n in GRID_CONFIG else DEFAULT_GRID_SIZE
        if self.available_sizes and preferred not in self.puzzles_by_size:
            preferred = self.available_sizes[0]

        self.set_level(preferred)

    def _init_fonts(self) -> None:
        self.title_font = pygame.font.SysFont(FONT_FAMILY, 40, bold=True)
        self.info_font = pygame.font.SysFont(FONT_FAMILY, FONT_INFO_SIZE)
        self.legend_font = pygame.font.SysFont(FONT_FAMILY, FONT_INFO_SIZE - 2)
        self.button_font = pygame.font.SysFont(FONT_FAMILY, FONT_BUTTON_SIZE - 8, bold=True)
        self.timer_font = pygame.font.SysFont(FONT_FAMILY, 30, bold=True)
        self.cell_font = pygame.font.SysFont(FONT_FAMILY, 38, bold=True)

    def _init_buttons(self) -> None:
        self.back_button = Button(pygame.Rect(30, 24, 132, 48), "Back", self.button_font)
        self.new_puzzle_button = Button(pygame.Rect(178, 24, 188, 48), "New Puzzle", self.button_font)
        self.timer = Timer()

    def set_level(self, n: int) -> None:
        if n not in GRID_CONFIG:
            n = DEFAULT_GRID_SIZE

        self.n = n
        cfg = GRID_CONFIG[n]
        self.cell_size = cfg["cell_size"]
        self.cell_gap = cfg["gap"]
        self.board_top = cfg["board_top"]
        self.container_padding = cfg["container_padding"]
        self.relation_size = cfg["relation_size"]
        self.relation_stroke = cfg["relation_stroke"]
        self.cell_font = pygame.font.SysFont(FONT_FAMILY, cfg["cell_font"], bold=True)

        self.case_index_by_size.setdefault(n, -1)
        self.case_index_by_size[n] = -1
        self.new_puzzle()

    def new_puzzle(self) -> None:
        """Load next puzzle from Inputs for the current board size."""
        cases = self.puzzles_by_size.get(self.n, [])
        if not cases:
            self.current_case = None
            self._init_empty_board()
            self.timer.start()
            self._revalidate_board()
            self.status_message = f"No puzzle file for level {self.n}x{self.n} in Inputs"
            return

        next_index = (self.case_index_by_size.get(self.n, -1) + 1) % len(cases)
        self.case_index_by_size[self.n] = next_index
        self._load_case(cases[next_index])

    def _init_empty_board(self) -> None:
        self.values = [[0 for _ in range(self.n)] for _ in range(self.n)]
        self.clues = {}
        self.horizontal_relations = {}
        self.vertical_relations = {}
        self.selected = None
        self._build_cells()

    def _load_case(self, case: PuzzleCase) -> None:
        self.current_case = case
        self.n = case.n

        self.values = [row[:] for row in case.grid]
        self.clues = {}
        for row in range(self.n):
            for col in range(self.n):
                value = case.grid[row][col]
                if value != 0:
                    self.clues[(row, col)] = value

        self.horizontal_relations = {}
        for row in range(self.n):
            for col in range(self.n - 1):
                rel = case.horizontal[row][col]
                if rel == 1:
                    self.horizontal_relations[(row, col)] = "<"
                elif rel == -1:
                    self.horizontal_relations[(row, col)] = ">"

        self.vertical_relations = {}
        for row in range(self.n - 1):
            for col in range(self.n):
                rel = case.vertical[row][col]
                if rel == 1:
                    self.vertical_relations[(row, col)] = "^"
                elif rel == -1:
                    self.vertical_relations[(row, col)] = "v"

        self.selected = None
        self._build_cells()
        self.timer.start()
        self._revalidate_board()
        self.status_message = f"Loaded {case.name}"

    def _build_cells(self) -> None:
        board_size = self.n * self.cell_size + (self.n - 1) * self.cell_gap
        board_left = (self.surface_rect.width - board_size) // 2
        board_top = self.board_top

        self.board_rect = pygame.Rect(
            board_left - self.container_padding,
            board_top - self.container_padding,
            board_size + self.container_padding * 2,
            board_size + self.container_padding * 2,
        )

        self.cells = []
        for row in range(self.n):
            row_cells: List[Cell] = []
            for col in range(self.n):
                x = board_left + col * (self.cell_size + self.cell_gap)
                y = board_top + row * (self.cell_size + self.cell_gap)

                row_cells.append(
                    Cell(
                        row=row,
                        col=col,
                        rect=pygame.Rect(x, y, self.cell_size, self.cell_size),
                        value=self.values[row][col],
                        is_clue=(row, col) in self.clues,
                    )
                )
            self.cells.append(row_cells)

    def handle_event(self, event: pygame.event.Event) -> Transition:
        if self.back_button.handle_event(event):
            self.timer.stop()
            return {"state": "level_select"}

        if self.new_puzzle_button.handle_event(event):
            self.new_puzzle()
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._select_cell(event.pos)

        if event.type == pygame.KEYDOWN:
            self._handle_input_key(event.key)

        return None

    def update(self, dt: float) -> None:
        self.timer.update(dt)

    def _select_cell(self, pos: Tuple[int, int]) -> None:
        self.selected = None
        for row_cells in self.cells:
            for cell in row_cells:
                cell.is_selected = False
                if cell.contains(pos):
                    cell.is_selected = True
                    self.selected = (cell.row, cell.col)

    def _handle_input_key(self, key: int) -> None:
        if self.selected is None:
            return

        row, col = self.selected
        cell = self.cells[row][col]
        if cell.is_clue:
            return

        if key in (pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_0, pygame.K_KP0):
            self.set_cell_value(row, col, 0)
            return

        value = None
        if pygame.K_1 <= key <= pygame.K_9:
            value = key - pygame.K_0
        elif pygame.K_KP1 <= key <= pygame.K_KP9:
            value = key - pygame.K_KP0

        if value is None:
            return

        if 1 <= value <= self.n:
            self.set_cell_value(row, col, value)

    def set_cell_value(self, row: int, col: int, value: int) -> None:
        """Set value for one cell and trigger immediate validation."""
        if not (0 <= row < self.n and 0 <= col < self.n):
            return

        if value < 0 or value > self.n:
            return

        cell = self.cells[row][col]
        if cell.is_clue:
            return

        self.values[row][col] = value
        cell.set_value(value)
        self._revalidate_board()

    def _mark_invalid(self, positions: List[Tuple[int, int]]) -> None:
        for row, col in positions:
            self.invalid_positions.add((row, col))

    def _validate_rows(self) -> None:
        # Validate row uniqueness and value domain.
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
        # Validate column uniqueness.
        for col in range(self.n):
            seen = {}
            for row in range(self.n):
                value = self.values[row][col]
                if value == 0:
                    continue
                seen.setdefault(value, []).append((row, col))

            for positions in seen.values():
                if len(positions) > 1:
                    self._mark_invalid(positions)

    def _validate_horizontal(self) -> None:
        # Validate horizontal inequalities.
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
            else:  # ">"
                if left == 1:
                    self.invalid_positions.add((row, col))
                if right == self.n:
                    self.invalid_positions.add((row, col + 1))
                if left != 0 and right != 0 and not (left > right):
                    self._mark_invalid([(row, col), (row, col + 1)])

    def _validate_vertical(self) -> None:
        # Validate vertical inequalities.
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
            else:  # "v"
                if top == 1:
                    self.invalid_positions.add((row, col))
                if bottom == self.n:
                    self.invalid_positions.add((row + 1, col))
                if top != 0 and bottom != 0 and not (top > bottom):
                    self._mark_invalid([(row, col), (row + 1, col)])

    def _revalidate_board(self) -> None:
        self.invalid_positions = set()

        self._validate_rows()
        self._validate_cols()
        self._validate_horizontal()
        self._validate_vertical()

        for row_cells in self.cells:
            for cell in row_cells:
                cell.is_invalid = (cell.row, cell.col) in self.invalid_positions

        if self.invalid_positions:
            self.status_message = "Invalid move: duplicate or inequality violation"
        elif self._is_filled():
            self.status_message = "Board is valid"
        else:
            self.status_message = "Board is valid, continue solving"

    def _is_filled(self) -> bool:
        return all(value != 0 for row in self.values for value in row)

    def _draw_timer(self, surface: pygame.Surface) -> None:
        timer_rect = pygame.Rect(self.surface_rect.width - 182, 22, 146, 52)
        pygame.draw.rect(surface, COLOR_PANEL, timer_rect, border_radius=16)
        pygame.draw.rect(surface, COLOR_BORDER, timer_rect, width=1, border_radius=16)

        timer_text = self.timer_font.render(self.timer.format_time(), True, COLOR_TITLE)
        surface.blit(timer_text, timer_text.get_rect(center=timer_rect.center))

    def _draw_relations(self, surface: pygame.Surface) -> None:
        for (row, col), symbol in self.horizontal_relations.items():
            left_cell = self.cells[row][col]
            right_cell = self.cells[row][col + 1]
            center = (
                (left_cell.rect.right + right_cell.rect.left) // 2,
                left_cell.rect.centery,
            )
            _draw_relation_symbol(surface, center, symbol, self.relation_size, self.relation_stroke)

        for (row, col), symbol in self.vertical_relations.items():
            top_cell = self.cells[row][col]
            bottom_cell = self.cells[row + 1][col]
            center = (
                top_cell.rect.centerx,
                (top_cell.rect.bottom + bottom_cell.rect.top) // 2,
            )
            _draw_relation_symbol(surface, center, symbol, self.relation_size, self.relation_stroke)

    def _draw_header(self, surface: pygame.Surface) -> None:
        title = self.title_font.render(f"Futoshiki {self.n}x{self.n}", True, COLOR_TITLE)
        subtitle = self.info_font.render("Input-driven puzzles with live validation", True, COLOR_MUTED)
        puzzle_name = self.legend_font.render(
            self.current_case.name if self.current_case is not None else "No puzzle file loaded",
            True,
            COLOR_MUTED,
        )

        surface.blit(title, (30, 90))
        surface.blit(subtitle, (30, 133))
        surface.blit(puzzle_name, (30, 165))

        self.back_button.draw(surface)
        self.new_puzzle_button.draw(surface)
        self._draw_timer(surface)

    def _draw_board(self, surface: pygame.Surface) -> None:
        board_shadow = self.board_rect.move(0, 10)
        pygame.draw.rect(
            surface,
            _mix(COLOR_SHADOW, COLOR_BACKGROUND, 0.24),
            board_shadow,
            border_radius=CONTAINER_RADIUS,
        )
        pygame.draw.rect(surface, COLOR_PANEL, self.board_rect, border_radius=CONTAINER_RADIUS)
        pygame.draw.rect(surface, COLOR_BORDER, self.board_rect, width=1, border_radius=CONTAINER_RADIUS)

        for row_cells in self.cells:
            for cell in row_cells:
                cell.draw(surface, self.cell_font)

        self._draw_relations(surface)

    def _draw_legend(self, surface: pygame.Surface) -> None:
        clue_legend = self.legend_font.render("Clue", True, COLOR_CLUE)
        solver_legend = self.legend_font.render("Player/Solver", True, COLOR_SOLVER)

        legend_y = self.surface_rect.height - 84
        legend_box = pygame.Rect(30, legend_y - 16, 430, 62)
        pygame.draw.rect(surface, COLOR_PANEL, legend_box, border_radius=16)
        pygame.draw.rect(surface, COLOR_BORDER, legend_box, width=1, border_radius=16)

        surface.blit(clue_legend, (48, legend_y))
        surface.blit(solver_legend, (148, legend_y))

    def _draw_status(self, surface: pygame.Surface) -> None:
        status_color = COLOR_ERROR if self.invalid_positions else COLOR_MUTED
        status_text = self.legend_font.render(self.status_message, True, status_color)

        legend_y = self.surface_rect.height - 84
        status_box = pygame.Rect(474, legend_y - 16, self.surface_rect.width - 504, 62)
        box_color = COLOR_PANEL if not self.invalid_positions else COLOR_SUCCESS_SOFT
        pygame.draw.rect(surface, box_color, status_box, border_radius=16)
        pygame.draw.rect(surface, COLOR_BORDER, status_box, width=1, border_radius=16)
        surface.blit(status_text, status_text.get_rect(midleft=(status_box.left + 18, status_box.centery)))

    def draw(self, surface: pygame.Surface) -> None:
        _draw_soft_background(surface)
        self._draw_header(surface)
        self._draw_board(surface)
        self._draw_legend(surface)
        self._draw_status(surface)
