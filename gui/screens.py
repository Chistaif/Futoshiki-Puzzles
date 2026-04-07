"""Menu, level selection, and gameplay screens for Futoshiki."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pygame

from .components import Button, Cell, Timer
from .constants import (
    BUTTON_HEIGHT,
    COLOR_BACKGROUND,
    COLOR_BORDER,
    COLOR_CLUE,
    COLOR_ERROR,
    COLOR_MUTED,
    COLOR_PANEL,
    COLOR_RELATION,
    COLOR_SHADOW,
    COLOR_SOLVER,
    COLOR_SUCCESS_SOFT,
    COLOR_TITLE,
    CONTAINER_RADIUS,
    DEFAULT_GRID_SIZE,
    FONT_BUTTON_SIZE,
    FONT_FAMILY,
    FONT_INFO_SIZE,
    FONT_SUBTITLE_SIZE,
    FONT_TITLE_SIZE,
    GRID_CONFIG,
    LEVEL_OPTIONS,
    MENU_IMAGE_CANDIDATES,
)

Transition = Optional[Dict[str, Any]]


@dataclass(frozen=True)
class PuzzleCase:
    """One puzzle loaded from an input text file."""

    name: str
    path: Path
    n: int
    grid: List[List[int]]
    horizontal: List[List[int]]
    vertical: List[List[int]]


def _mix(color_a: Tuple[int, int, int], color_b: Tuple[int, int, int], ratio: float) -> Tuple[int, int, int]:
    ratio = max(0.0, min(1.0, ratio))
    return (
        int(color_a[0] + (color_b[0] - color_a[0]) * ratio),
        int(color_a[1] + (color_b[1] - color_a[1]) * ratio),
        int(color_a[2] + (color_b[2] - color_a[2]) * ratio),
    )


def _load_menu_background() -> Optional[pygame.Surface]:
    root_path = Path(__file__).resolve().parents[1]
    for parts in MENU_IMAGE_CANDIDATES:
        candidate = root_path.joinpath(*parts)
        if candidate.exists():
            return pygame.image.load(candidate.as_posix()).convert()
    return None


def _draw_soft_background(surface: pygame.Surface) -> None:
    surface.fill(COLOR_BACKGROUND)

    width, height = surface.get_size()
    layers = [
        (int(width * 0.82), int(height * 0.12), 180, (224, 232, 244, 80)),
        (int(width * 0.18), int(height * 0.86), 220, (218, 229, 240, 96)),
        (int(width * 0.58), int(height * 0.44), 260, (230, 236, 245, 72)),
    ]

    for x, y, radius, color in layers:
        blob = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(blob, color, (radius, radius), radius)
        surface.blit(blob, (x - radius, y - radius))


def _draw_relation_symbol(
    surface: pygame.Surface,
    center: Tuple[int, int],
    symbol: str,
    size: int,
    stroke: int,
) -> None:
    cx, cy = center
    half = size // 2

    if symbol == "<":
        points = [(cx + half, cy - half), (cx - half, cy), (cx + half, cy + half)]
    elif symbol == ">":
        points = [(cx - half, cy - half), (cx + half, cy), (cx - half, cy + half)]
    elif symbol == "^":
        points = [(cx - half, cy + half), (cx, cy - half), (cx + half, cy + half)]
    else:  # "v"
        points = [(cx - half, cy - half), (cx, cy + half), (cx + half, cy - half)]

    pygame.draw.line(surface, COLOR_RELATION, points[0], points[1], stroke)
    pygame.draw.line(surface, COLOR_RELATION, points[1], points[2], stroke)


def _parse_csv_ints(raw_line: str) -> List[int]:
    parts = [part.strip() for part in raw_line.split(",")]
    if any(part == "" for part in parts):
        raise ValueError(f"Invalid CSV line: {raw_line}")
    return [int(part) for part in parts]


def _read_clean_lines(path: Path) -> List[str]:
    raw_lines = path.read_text(encoding="utf-8").splitlines()
    cleaned: List[str] = []
    for line in raw_lines:
        content = line.strip()
        if not content:
            continue
        if content.startswith("#"):
            continue
        cleaned.append(content)
    return cleaned


def _parse_input_file(path: Path) -> PuzzleCase:
    lines = _read_clean_lines(path)
    if not lines:
        raise ValueError(f"Empty puzzle file: {path}")

    n = int(lines[0])
    expected_lines = 1 + n + n + (n - 1)
    if len(lines) < expected_lines:
        raise ValueError(
            f"Puzzle file {path.name} is incomplete: expected at least {expected_lines} non-empty lines"
        )

    cursor = 1

    grid: List[List[int]] = []
    for _ in range(n):
        row = _parse_csv_ints(lines[cursor])
        cursor += 1
        if len(row) != n:
            raise ValueError(f"Grid row width mismatch in {path.name}")
        if any(value < 0 or value > n for value in row):
            raise ValueError(f"Grid value out of range [0, {n}] in {path.name}")
        grid.append(row)

    horizontal: List[List[int]] = []
    for _ in range(n):
        row = _parse_csv_ints(lines[cursor])
        cursor += 1
        if len(row) != n - 1:
            raise ValueError(f"Horizontal row width mismatch in {path.name}")
        if any(value not in (-1, 0, 1) for value in row):
            raise ValueError(f"Horizontal constraint must be -1, 0 or 1 in {path.name}")
        horizontal.append(row)

    vertical: List[List[int]] = []
    for _ in range(n - 1):
        row = _parse_csv_ints(lines[cursor])
        cursor += 1
        if len(row) != n:
            raise ValueError(f"Vertical row width mismatch in {path.name}")
        if any(value not in (-1, 0, 1) for value in row):
            raise ValueError(f"Vertical constraint must be -1, 0 or 1 in {path.name}")
        vertical.append(row)

    return PuzzleCase(
        name=path.name,
        path=path,
        n=n,
        grid=grid,
        horizontal=horizontal,
        vertical=vertical,
    )


def load_all_input_puzzles() -> List[PuzzleCase]:
    """Load and validate all puzzle files from Inputs directory."""
    root_path = Path(__file__).resolve().parents[1]
    input_dir = root_path / "Inputs"

    if not input_dir.exists():
        return []

    puzzle_cases: List[PuzzleCase] = []
    for file_path in sorted(input_dir.glob("*.txt")):
        try:
            puzzle_cases.append(_parse_input_file(file_path))
        except ValueError:
            # Skip malformed files so the UI can still run with valid ones.
            continue

    return puzzle_cases


class MenuScreen:
    """Landing screen with hero background and Play CTA."""

    def __init__(self, surface_rect: pygame.Rect) -> None:
        self.surface_rect = surface_rect
        self.background_image = _load_menu_background()

        self.title_font = pygame.font.SysFont(FONT_FAMILY, FONT_TITLE_SIZE + 6, bold=True)
        self.subtitle_font = pygame.font.SysFont(FONT_FAMILY, FONT_SUBTITLE_SIZE)
        self.button_font = pygame.font.SysFont(FONT_FAMILY, FONT_BUTTON_SIZE, bold=True)

        button_rect = pygame.Rect(0, 0, 230, BUTTON_HEIGHT)
        button_rect.center = (surface_rect.centerx, surface_rect.centery + 108)
        self.play_button = Button(button_rect, "Play", self.button_font)

    def handle_event(self, event: pygame.event.Event) -> Transition:
        if self.play_button.handle_event(event):
            return {"state": "level_select"}
        return None

    def update(self, _dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        if self.background_image is not None:
            image = pygame.transform.smoothscale(self.background_image, self.surface_rect.size)
            surface.blit(image, (0, 0))
        else:
            _draw_soft_background(surface)

        overlay = pygame.Surface(self.surface_rect.size, pygame.SRCALPHA)
        overlay.fill((20, 28, 38, 108))
        surface.blit(overlay, (0, 0))

        card = pygame.Rect(0, 0, 560, 340)
        card.center = self.surface_rect.center
        panel = pygame.Surface(card.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, (255, 255, 255, 190), panel.get_rect(), border_radius=32)
        surface.blit(panel, card.topleft)

        title = self.title_font.render("FUTOSHIKI", True, COLOR_TITLE)
        title_rect = title.get_rect(center=(card.centerx, card.top + 120))
        surface.blit(title, title_rect)

        subtitle = self.subtitle_font.render("Modern Flat Puzzle Experience", True, COLOR_MUTED)
        subtitle_rect = subtitle.get_rect(center=(card.centerx, card.top + 170))
        surface.blit(subtitle, subtitle_rect)

        self.play_button.draw(surface)


class LevelSelectScreen:
    """Screen where users choose board size before starting."""

    def __init__(self, surface_rect: pygame.Rect, available_sizes: Optional[Tuple[int, ...]] = None) -> None:
        self.surface_rect = surface_rect
        self.title_font = pygame.font.SysFont(FONT_FAMILY, FONT_TITLE_SIZE - 6, bold=True)
        self.subtitle_font = pygame.font.SysFont(FONT_FAMILY, FONT_SUBTITLE_SIZE)
        self.button_font = pygame.font.SysFont(FONT_FAMILY, FONT_BUTTON_SIZE - 2, bold=True)
        self.hint_font = pygame.font.SysFont(FONT_FAMILY, FONT_INFO_SIZE - 2)

        self.back_button = Button(pygame.Rect(34, 28, 132, 50), "Back", self.button_font)

        if available_sizes:
            self.level_options = tuple(sorted(available_sizes))
        else:
            self.level_options = LEVEL_OPTIONS

        self.level_buttons: List[Tuple[int, Button]] = []
        self._build_level_buttons()

    def _build_level_buttons(self) -> None:
        self.level_buttons.clear()

        columns = 3
        spacing_x = 28
        spacing_y = 28
        button_width = 200
        button_height = 86

        total_width = columns * button_width + (columns - 1) * spacing_x
        start_x = (self.surface_rect.width - total_width) // 2
        start_y = 240

        for index, size in enumerate(self.level_options):
            row = index // columns
            col = index % columns
            x = start_x + col * (button_width + spacing_x)
            y = start_y + row * (button_height + spacing_y)

            button = Button(
                pygame.Rect(x, y, button_width, button_height),
                f"{size} x {size}",
                self.button_font,
            )
            self.level_buttons.append((size, button))

    def handle_event(self, event: pygame.event.Event) -> Transition:
        if self.back_button.handle_event(event):
            return {"state": "menu"}

        for size, button in self.level_buttons:
            if button.handle_event(event):
                return {"state": "game", "level": size}

        return None

    def update(self, _dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        _draw_soft_background(surface)

        title = self.title_font.render("Select Level", True, COLOR_TITLE)
        subtitle = self.subtitle_font.render("Choose puzzle size from available inputs", True, COLOR_MUTED)

        surface.blit(title, title.get_rect(center=(self.surface_rect.centerx, 110)))
        surface.blit(subtitle, subtitle.get_rect(center=(self.surface_rect.centerx, 156)))

        panel_rect = pygame.Rect(0, 0, 760, 390)
        panel_rect.center = (self.surface_rect.centerx, self.surface_rect.centery + 38)

        shadow = panel_rect.move(0, 8)
        pygame.draw.rect(surface, _mix(COLOR_SHADOW, COLOR_BACKGROUND, 0.22), shadow, border_radius=26)
        pygame.draw.rect(surface, COLOR_PANEL, panel_rect, border_radius=26)
        pygame.draw.rect(surface, COLOR_BORDER, panel_rect, width=1, border_radius=26)

        self.back_button.draw(surface)

        if self.level_buttons:
            for _, button in self.level_buttons:
                button.draw(surface)
        else:
            no_data = self.hint_font.render("No valid puzzle file found in Inputs", True, COLOR_ERROR)
            surface.blit(no_data, no_data.get_rect(center=panel_rect.center))


class GameScreen:
    """Main gameplay scene with live validation and file-based puzzles."""

    def __init__(self, surface_rect: pygame.Rect, n: int = DEFAULT_GRID_SIZE) -> None:
        self.surface_rect = surface_rect

        self.title_font = pygame.font.SysFont(FONT_FAMILY, 40, bold=True)
        self.info_font = pygame.font.SysFont(FONT_FAMILY, FONT_INFO_SIZE)
        self.legend_font = pygame.font.SysFont(FONT_FAMILY, FONT_INFO_SIZE - 2)
        self.button_font = pygame.font.SysFont(FONT_FAMILY, FONT_BUTTON_SIZE - 8, bold=True)
        self.timer_font = pygame.font.SysFont(FONT_FAMILY, 30, bold=True)

        self.back_button = Button(pygame.Rect(30, 24, 132, 48), "Back", self.button_font)
        self.new_puzzle_button = Button(pygame.Rect(178, 24, 188, 48), "New Puzzle", self.button_font)
        self.timer = Timer()

        self.n = n
        self.cell_size = 80
        self.cell_gap = 20
        self.relation_size = 18
        self.relation_stroke = 4
        self.container_padding = 24
        self.board_top = 140

        self.cell_font = pygame.font.SysFont(FONT_FAMILY, 38, bold=True)

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

    def _revalidate_board(self) -> None:
        self.invalid_positions = set()

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

    def draw(self, surface: pygame.Surface) -> None:
        _draw_soft_background(surface)

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

        clue_legend = self.legend_font.render("Clue", True, COLOR_CLUE)
        solver_legend = self.legend_font.render("Player/Solver", True, COLOR_SOLVER)
        status_color = COLOR_ERROR if self.invalid_positions else COLOR_MUTED
        status_text = self.legend_font.render(self.status_message, True, status_color)

        legend_y = self.surface_rect.height - 84
        legend_box = pygame.Rect(30, legend_y - 16, 430, 62)
        pygame.draw.rect(surface, COLOR_PANEL, legend_box, border_radius=16)
        pygame.draw.rect(surface, COLOR_BORDER, legend_box, width=1, border_radius=16)

        surface.blit(clue_legend, (48, legend_y))
        surface.blit(solver_legend, (148, legend_y))

        status_box = pygame.Rect(474, legend_y - 16, self.surface_rect.width - 504, 62)
        box_color = COLOR_PANEL if not self.invalid_positions else COLOR_SUCCESS_SOFT
        pygame.draw.rect(surface, box_color, status_box, border_radius=16)
        pygame.draw.rect(surface, COLOR_BORDER, status_box, width=1, border_radius=16)
        surface.blit(status_text, status_text.get_rect(midleft=(status_box.left + 18, status_box.centery)))
