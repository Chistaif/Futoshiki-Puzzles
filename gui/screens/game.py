"""Minimalist gameplay screen for Futoshiki."""

from __future__ import annotations

import threading
from collections import deque
from queue import Empty, Queue
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional, Tuple

import pygame

from file import PuzzleCase, load_all_input_puzzles
from solvers.astar import AStarSolver
from solvers.backtrack import Backtracking

from ..components import Button, Cell, Timer
from ..constants import (
    COLOR_BUTTON,
    COLOR_BUTTON_HOVER,
    COLOR_BUTTON_TEXT,
    COLOR_GAME_ACCENT,
    COLOR_GAME_BACKGROUND,
    COLOR_GAME_BACKGROUND_SHADE,
    COLOR_GAME_MUTED,
    COLOR_GAME_PANEL,
    COLOR_GAME_PANEL_BORDER,
    COLOR_GAME_TEXT,
    COLOR_RELATION_ACTIVE,
    COLOR_RELATION_IDLE,
    CONTAINER_RADIUS,
    DEFAULT_GRID_SIZE,
    FONT_BUTTON_SIZE,
    FONT_FAMILY,
    FONT_INFO_SIZE,
    GRID_CONFIG,
)
from ..utils import _draw_relation_symbol, _mix

Transition = Optional[Dict[str, Any]]


class GameScreen:
    """Main gameplay screen with optional AI solver animation."""

    def __init__(self, surface_rect: pygame.Rect, n: int = DEFAULT_GRID_SIZE) -> None:
        self.surface_rect = surface_rect
        self.layout_margin = max(16, int(self.surface_rect.width * 0.03))
        self.header_rect = pygame.Rect(0, 0, 100, 44)

        self._init_fonts()
        self._init_buttons()

        self.n = n
        self.cell_size = 80
        self.cell_gap = 20
        self.relation_size = 16
        self.relation_stroke = 2
        self.container_padding = 20

        self.values: List[List[int]] = []
        self.clues: Dict[Tuple[int, int], int] = {}
        self.horizontal_relations: Dict[Tuple[int, int], str] = {}
        self.vertical_relations: Dict[Tuple[int, int], str] = {}
        self.cells: List[List[Cell]] = []
        self.selected: Optional[Tuple[int, int]] = None
        self.invalid_positions: set[Tuple[int, int]] = set()

        self.current_case: Optional[PuzzleCase] = None
        self.status_message = "Ready"
        self.board_rect = pygame.Rect(0, 0, 100, 100)
        self.screen_mode = "play"

        self.ai_trace: List[Tuple[int, int, int]] = []
        self.ai_pending_steps: Deque[Tuple[int, int, int]] = deque()
        self.ai_step_index = 0
        self.ai_step_elapsed = 0.0
        self.ai_step_delay_ms = 75
        self.ai_step_interval = self.ai_step_delay_ms / 1000.0
        self.ai_animating = False
        self.ai_solver_name = ""
        self.ai_solver_running = False
        self.ai_solver_done = False
        self.ai_solver_found_solution = False
        self.ai_worker_thread: Optional[threading.Thread] = None
        self.ai_worker_cancel_event = threading.Event()
        self.ai_event_queue: Queue[Tuple[str, Any]] = Queue()
        self.ai_focus_cell: Optional[Tuple[int, int]] = None
        self.ai_focus_backtrack = False
        self.ai_dirty_cells: set[Tuple[int, int]] = set()
        self.force_full_draw = True

        self.ai_click_sound: Optional[pygame.mixer.Sound] = None
        self._init_audio()

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
        self.button_font = pygame.font.SysFont(FONT_FAMILY, FONT_BUTTON_SIZE - 8, bold=True)
        self.status_font = pygame.font.SysFont(FONT_FAMILY, FONT_INFO_SIZE - 8, bold=True)
        self.meta_font = pygame.font.SysFont(FONT_FAMILY, FONT_INFO_SIZE - 10)
        self.cell_font = pygame.font.SysFont(FONT_FAMILY, 38, bold=True)

    def _init_buttons(self) -> None:
        self.back_button = Button(
            pygame.Rect(0, 0, 88, 44),
            "",
            self.button_font,
            bg_color=COLOR_BUTTON,
            hover_color=COLOR_BUTTON_HOVER,
            text_color=COLOR_BUTTON_TEXT,
        )
        self.timer = Timer()

    def _init_audio(self) -> None:
        root_path = Path(__file__).resolve().parents[2]
        candidates = (
            ("assets", "btn_click.mp3"),
            ("assets", "click.wav"),
            ("assets", "picture", "btn_click.mp3"),
        )

        for parts in candidates:
            sound_path = root_path.joinpath(*parts)
            if not sound_path.exists():
                continue

            try:
                if pygame.mixer.get_init() is None:
                    pygame.mixer.init()
                self.ai_click_sound = pygame.mixer.Sound(sound_path.as_posix())
                self.ai_click_sound.set_volume(0.2)
            except pygame.error:
                self.ai_click_sound = None
            return

    def _update_layout(self) -> None:
        self.layout_margin = max(16, int(self.surface_rect.width * 0.03))

        self.back_button.rect.topleft = (self.layout_margin, self.layout_margin)

        header_left = self.back_button.rect.right + 12
        header_width = max(130, self.surface_rect.width - self.layout_margin - header_left)
        self.header_rect = pygame.Rect(
            header_left,
            self.back_button.rect.top,
            header_width,
            self.back_button.rect.height,
        )

    def _clear_ai_focus(self) -> None:
        for row_cells in self.cells:
            for cell in row_cells:
                cell.is_ai_focus = False
                cell.is_ai_backtrack = False

    def _set_ai_focus(self, pos: Optional[Tuple[int, int]], is_backtrack: bool) -> None:
        self.ai_focus_cell = pos
        self.ai_focus_backtrack = is_backtrack
        self._clear_ai_focus()

        if pos is None:
            return

        row, col = pos
        if not (0 <= row < len(self.cells) and 0 <= col < len(self.cells[row])):
            return

        cell = self.cells[row][col]
        cell.is_ai_focus = True
        cell.is_ai_backtrack = is_backtrack

    def _solver_key_from_name(self) -> str:
        name = self.ai_solver_name.lower().strip()
        if "a*" in name or "astar" in name:
            return "astar"
        return "backtracking"

    def set_mode(self, mode: str) -> None:
        self.screen_mode = "ai" if str(mode).lower() == "ai" else "play"

    def shutdown(self) -> None:
        self._stop_ai_worker(wait_timeout=0.25)

    def set_level(self, n: int, case_name: Optional[str] = None) -> None:
        self._reset_ai_animation()
        if n not in GRID_CONFIG:
            n = DEFAULT_GRID_SIZE

        self.n = n
        cfg = GRID_CONFIG[n]
        self.cell_size = cfg["cell_size"]
        self.cell_gap = cfg["gap"]
        self.container_padding = cfg["container_padding"]
        self.relation_size = cfg["relation_size"]
        self.relation_stroke = cfg["relation_stroke"]
        self.cell_font = pygame.font.SysFont(FONT_FAMILY, cfg["cell_font"], bold=True)

        self.case_index_by_size.setdefault(n, -1)

        if case_name:
            case = self._find_case_by_name(n, case_name)
            if case is not None:
                self._load_case(case)
                return

        self.case_index_by_size[n] = -1
        self.new_puzzle()

    def _find_case_by_name(self, n: int, case_name: str) -> Optional[PuzzleCase]:
        target = case_name.strip().lower()
        if not target:
            return None

        cases = self.puzzles_by_size.get(n, [])
        for index, case in enumerate(cases):
            if case.name.lower() == target or case.path.name.lower() == target:
                self.case_index_by_size[n] = index
                return case
        return None

    def new_puzzle(self) -> None:
        self._reset_ai_animation()
        cases = self.puzzles_by_size.get(self.n, [])
        if not cases:
            self.current_case = None
            self._init_empty_board()
            self.timer.start()
            self._revalidate_board(keep_status=True)
            self.status_message = f"No puzzle file for {self.n}x{self.n}"
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
        self.force_full_draw = True
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
        self.force_full_draw = True
        self._build_cells()
        self.timer.start()
        self._revalidate_board(keep_status=True)
        self.status_message = f"Loaded {case.name}"

    def _build_cells(self) -> None:
        self._update_layout()

        board_size = self.n * self.cell_size + (self.n - 1) * self.cell_gap
        board_left = (self.surface_rect.width - board_size) // 2

        usable_top = self.back_button.rect.bottom + 24
        usable_bottom = self.surface_rect.height - self.layout_margin - 20
        usable_height = max(0, usable_bottom - usable_top)
        board_top = usable_top + max(0, (usable_height - board_size) // 2)

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

        self._set_ai_focus(self.ai_focus_cell, self.ai_focus_backtrack)
        self.force_full_draw = True

    def handle_event(self, event: pygame.event.Event) -> Transition:
        self._update_layout()

        if self.back_button.handle_event(event):
            solver_key = self._solver_key_from_name()
            self._reset_ai_animation()
            self.timer.stop()
            return {
                "state": "deal_select",
                "mode": self.screen_mode,
                "solver_name": solver_key,
            }

        if self.ai_animating:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._select_cell(event.pos)

        if event.type == pygame.KEYDOWN:
            self._handle_input_key(event.key)

        return None

    def update(self, dt: float) -> None:
        self.timer.update(dt)
        self._drain_ai_events()

        if not self.ai_animating:
            return

        self.ai_step_elapsed += dt
        while self.ai_step_elapsed >= self.ai_step_interval and self.ai_animating:
            self.ai_step_elapsed -= self.ai_step_interval
            self._apply_next_ai_step()

        if not self.ai_pending_steps and self.ai_solver_done:
            self.ai_animating = False
            self._set_ai_focus(None, False)
            if self.ai_solver_found_solution and self._is_filled() and not self.invalid_positions:
                self.status_message = "Solved"
                self.timer.stop()
            elif self.ai_solver_found_solution:
                self.status_message = "Completed"
            else:
                self.status_message = "No solution found"
            self.force_full_draw = True

    def _reset_ai_animation(self) -> None:
        self._stop_ai_worker(wait_timeout=0.15)
        self.ai_trace = []
        self.ai_pending_steps = deque()
        self.ai_step_index = 0
        self.ai_step_elapsed = 0.0
        self.ai_animating = False
        self.ai_solver_running = False
        self.ai_solver_done = False
        self.ai_solver_found_solution = False
        self.ai_solver_name = ""
        self.ai_event_queue = Queue()
        self.ai_dirty_cells.clear()
        self.force_full_draw = True
        self._set_ai_focus(None, False)

    def start_ai_solver(self, case: PuzzleCase, solver_name: str = "backtracking") -> None:
        normalized_solver = str(solver_name).strip().lower()
        if normalized_solver in ("a*", "a_star"):
            normalized_solver = "astar"

        if normalized_solver not in ("backtracking", "astar"):
            self.status_message = f"Unsupported solver: {solver_name}"
            return

        self.set_mode("ai")
        self.set_level(case.n, case.name)

        active_case = self.current_case if self.current_case is not None else case

        self.ai_solver_name = "A* Search" if normalized_solver == "astar" else "Backtracking"
        self.ai_trace = []
        self.ai_pending_steps = deque()
        self.ai_step_index = 0
        self.ai_step_elapsed = 0.0
        self.ai_solver_done = False
        self.ai_solver_found_solution = False
        self.ai_solver_running = True
        self.ai_animating = True
        self.status_message = f"Thinking ({self.ai_solver_name})..."
        self._start_ai_worker(active_case, normalized_solver)

    def _start_ai_worker(self, case: PuzzleCase, solver_name: str) -> None:
        self._stop_ai_worker(wait_timeout=0.05)
        event_queue: Queue[Tuple[str, Any]] = Queue()
        cancel_event = threading.Event()
        self.ai_event_queue = event_queue
        self.ai_worker_cancel_event = cancel_event

        worker = threading.Thread(
            target=self._run_solver_worker,
            args=(case, solver_name, event_queue, cancel_event),
            daemon=True,
        )
        self.ai_worker_thread = worker
        worker.start()

    def _run_solver_worker(
        self,
        case: PuzzleCase,
        solver_name: str,
        event_queue: Queue[Tuple[str, Any]],
        cancel_event: threading.Event,
    ) -> None:
        try:
            def on_step(row: int, col: int, value: int) -> None:
                if cancel_event.is_set():
                    raise RuntimeError("solver-cancelled")
                event_queue.put(("step", (row, col, value)))

            if solver_name == "astar":
                solver = AStarSolver(case, use_ac3=True, emit_search_trace=True)
            else:
                solver = Backtracking(case)

            solved_grid = solver.solve(step_callback=on_step)
            if cancel_event.is_set():
                event_queue.put(("cancelled", None))
                return

            event_queue.put(("done", solved_grid is not None))
        except RuntimeError as exc:
            if str(exc) == "solver-cancelled":
                event_queue.put(("cancelled", None))
                return
            event_queue.put(("error", str(exc)))
        except Exception as exc:  # pragma: no cover
            event_queue.put(("error", str(exc)))

    def _stop_ai_worker(self, wait_timeout: float) -> None:
        self.ai_worker_cancel_event.set()
        worker = self.ai_worker_thread
        if worker is not None and worker.is_alive():
            worker.join(timeout=wait_timeout)
        self.ai_worker_thread = None

    def _drain_ai_events(self) -> None:
        while True:
            try:
                event_type, payload = self.ai_event_queue.get_nowait()
            except Empty:
                break

            if event_type == "step":
                row, col, value = payload
                self.ai_pending_steps.append((row, col, value))
                continue

            if event_type == "done":
                self.ai_solver_running = False
                self.ai_solver_done = True
                self.ai_solver_found_solution = bool(payload)
                continue

            if event_type == "cancelled":
                self.ai_solver_running = False
                self.ai_solver_done = True
                self.ai_solver_found_solution = False
                self.ai_pending_steps = deque()
                self.ai_animating = False
                self.status_message = "Solver cancelled"
                continue

            if event_type == "error":
                self.ai_solver_running = False
                self.ai_solver_done = True
                self.ai_solver_found_solution = False
                self.ai_pending_steps = deque()
                self.ai_animating = False
                self.status_message = f"Solver error: {payload}"

    def _play_ai_click(self) -> None:
        if self.ai_click_sound is None:
            return
        try:
            self.ai_click_sound.play()
        except pygame.error:
            pass

    def _apply_next_ai_step(self) -> None:
        if not self.ai_pending_steps:
            return

        row, col, value = self.ai_pending_steps.popleft()

        is_backtrack = value == 0
        self._set_ai_focus((row, col), is_backtrack)
        self.render_step(row, col, value)

        if value != 0:
            self._play_ai_click()
            self.status_message = f"Thinking ({self.ai_solver_name})..."
        else:
            if self._solver_key_from_name() == "backtracking":
                self.status_message = "Backtracking..."
            else:
                self.status_message = f"Thinking ({self.ai_solver_name})..."

    def render_step(self, row: int, col: int, value: int) -> None:
        """Apply one AI step and mark only impacted cells for incremental redraw."""
        if not (0 <= row < self.n and 0 <= col < self.n):
            return

        if value < 0 or value > self.n:
            return

        target_cell = self.cells[row][col]
        if target_cell.is_clue:
            return

        self.values[row][col] = value
        target_cell.set_value(value)
        self._revalidate_board(keep_status=True)
        self._mark_delta_cells(row, col)

    def _mark_delta_cells(self, row: int, col: int) -> None:
        self.ai_dirty_cells.add((row, col))
        if row > 0:
            self.ai_dirty_cells.add((row - 1, col))
        if row < self.n - 1:
            self.ai_dirty_cells.add((row + 1, col))
        if col > 0:
            self.ai_dirty_cells.add((row, col - 1))
        if col < self.n - 1:
            self.ai_dirty_cells.add((row, col + 1))

    def _draw_incremental_board(self, surface: pygame.Surface) -> None:
        if not self.ai_dirty_cells:
            return

        clear_rects: List[pygame.Rect] = []
        for row, col in self.ai_dirty_cells:
            cell_rect = self.cells[row][col].rect.inflate(self.cell_gap + 10, self.cell_gap + 10)
            clipped = cell_rect.clip(self.board_rect)
            if clipped.width > 0 and clipped.height > 0:
                clear_rects.append(clipped)

        for rect in clear_rects:
            pygame.draw.rect(surface, COLOR_GAME_PANEL, rect)

        for row, col in self.ai_dirty_cells:
            self.cells[row][col].draw(surface, self.cell_font)

        # Redraw relation symbols to keep inequality marks in sync with updated values.
        self._draw_relations(surface)
        self.ai_dirty_cells.clear()

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

    def set_cell_value(self, row: int, col: int, value: int, keep_status: bool = False) -> None:
        if not (0 <= row < self.n and 0 <= col < self.n):
            return

        if value < 0 or value > self.n:
            return

        cell = self.cells[row][col]
        if cell.is_clue:
            return

        self.values[row][col] = value
        cell.set_value(value)
        self._revalidate_board(keep_status=keep_status)

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

    def _revalidate_board(self, keep_status: bool = False) -> None:
        self.invalid_positions = set()

        self._validate_rows()
        self._validate_cols()
        self._validate_horizontal()
        self._validate_vertical()

        for row_cells in self.cells:
            for cell in row_cells:
                cell.is_invalid = (cell.row, cell.col) in self.invalid_positions

        if keep_status:
            return

        if self.invalid_positions:
            self.status_message = "Invalid move"
        elif self._is_filled():
            self.status_message = "Board valid"
        else:
            self.status_message = "Editing"

    def _is_filled(self) -> bool:
        return all(value != 0 for row in self.values for value in row)

    @staticmethod
    def _relation_is_satisfied(symbol: str, left_value: int, right_value: int) -> bool:
        if left_value == 0 or right_value == 0:
            return False

        if symbol in ("<", "^"):
            return left_value < right_value

        return left_value > right_value

    def _draw_relations(self, surface: pygame.Surface) -> None:
        for (row, col), symbol in self.horizontal_relations.items():
            left_cell = self.cells[row][col]
            right_cell = self.cells[row][col + 1]
            left_value = self.values[row][col]
            right_value = self.values[row][col + 1]
            center = (
                (left_cell.rect.right + right_cell.rect.left) // 2,
                left_cell.rect.centery,
            )
            relation_color = (
                COLOR_RELATION_ACTIVE
                if self._relation_is_satisfied(symbol, left_value, right_value)
                else COLOR_RELATION_IDLE
            )
            _draw_relation_symbol(
                surface,
                center,
                symbol,
                self.relation_size,
                self.relation_stroke,
                color=relation_color,
            )

        for (row, col), symbol in self.vertical_relations.items():
            top_cell = self.cells[row][col]
            bottom_cell = self.cells[row + 1][col]
            top_value = self.values[row][col]
            bottom_value = self.values[row + 1][col]
            center = (
                top_cell.rect.centerx,
                (top_cell.rect.bottom + bottom_cell.rect.top) // 2,
            )
            relation_color = (
                COLOR_RELATION_ACTIVE
                if self._relation_is_satisfied(symbol, top_value, bottom_value)
                else COLOR_RELATION_IDLE
            )
            _draw_relation_symbol(
                surface,
                center,
                symbol,
                self.relation_size,
                self.relation_stroke,
                color=relation_color,
            )

    @staticmethod
    def _truncate_text(font: pygame.font.Font, text: str, max_width: int) -> str:
        if max_width <= 12:
            return ""

        if font.size(text)[0] <= max_width:
            return text

        suffix = "..."
        raw = text
        while raw and font.size(raw + suffix)[0] > max_width:
            raw = raw[:-1]
        return (raw + suffix) if raw else suffix

    def _draw_background(self, surface: pygame.Surface) -> None:
        surface.fill(COLOR_GAME_BACKGROUND)

        width, height = surface.get_size()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)

        blob_a = (*_mix(COLOR_GAME_BACKGROUND_SHADE, (255, 255, 255), 0.2), 180)
        blob_b = (*_mix(COLOR_GAME_BACKGROUND_SHADE, COLOR_GAME_PANEL_BORDER, 0.35), 130)
        blob_c = (*_mix(COLOR_GAME_BACKGROUND, (255, 255, 255), 0.55), 95)

        radius = max(80, int(min(width, height) * 0.32))
        pygame.draw.circle(overlay, blob_a, (int(width * 0.14), int(height * 0.16)), radius)
        pygame.draw.circle(overlay, blob_b, (int(width * 0.86), int(height * 0.84)), int(radius * 1.15))
        pygame.draw.circle(overlay, blob_c, (int(width * 0.84), int(height * 0.18)), int(radius * 0.6))

        surface.blit(overlay, (0, 0))

    def _draw_info_pill_right(
        self,
        surface: pygame.Surface,
        text: str,
        right: int,
        top: int,
        accent: bool = False,
    ) -> int:
        label_color = (250, 252, 255) if accent else COLOR_GAME_TEXT
        label = self.meta_font.render(text, True, label_color)

        width = label.get_width() + 18
        rect = pygame.Rect(right - width, top, width, 28)
        fill = COLOR_GAME_ACCENT if accent else _mix(COLOR_GAME_PANEL, COLOR_GAME_BACKGROUND, 0.06)
        border = COLOR_GAME_ACCENT if accent else COLOR_GAME_PANEL_BORDER

        pygame.draw.rect(surface, fill, rect, border_radius=14)
        pygame.draw.rect(surface, border, rect, width=1, border_radius=14)
        surface.blit(label, label.get_rect(center=rect.center))
        return rect.left - 8

    def _draw_header(self, surface: pygame.Surface) -> None:
        self.back_button.draw(surface)

        icon_color = COLOR_BUTTON_TEXT
        cx, cy = self.back_button.rect.center
        pygame.draw.polygon(
            surface,
            icon_color,
            [
                (cx - 12, cy),
                (cx + 6, cy - 10),
                (cx + 6, cy + 10),
            ],
        )

        header_shadow = self.header_rect.move(0, 3)
        pygame.draw.rect(
            surface,
            _mix(COLOR_GAME_PANEL_BORDER, COLOR_GAME_BACKGROUND_SHADE, 0.35),
            header_shadow,
            border_radius=16,
        )
        pygame.draw.rect(surface, COLOR_GAME_PANEL, self.header_rect, border_radius=16)
        pygame.draw.rect(surface, COLOR_GAME_PANEL_BORDER, self.header_rect, width=1, border_radius=16)

        chip_top = self.header_rect.top + (self.header_rect.height - 28) // 2
        right_cursor = self.header_rect.right - 12
        right_cursor = self._draw_info_pill_right(surface, self.timer.format_time(), right_cursor, chip_top)
        mode_label = "AI" if self.screen_mode == "ai" else "PLAY"
        right_cursor = self._draw_info_pill_right(
            surface,
            mode_label,
            right_cursor,
            chip_top,
            accent=(self.screen_mode == "ai"),
        )

        left_x = self.header_rect.left + 12
        max_text_width = max(70, right_cursor - left_x - 6)

        if self.current_case is not None:
            case_label = Path(self.current_case.name).stem.replace("_", "-")
        else:
            case_label = f"Deal {self.n}x{self.n}"

        case_label = self._truncate_text(self.status_font, case_label, max_text_width)
        status_text = self._truncate_text(self.meta_font, self.status_message, max_text_width)

        case_surface = self.status_font.render(case_label, True, COLOR_GAME_TEXT)
        status_surface = self.meta_font.render(status_text, True, COLOR_GAME_MUTED)

        surface.blit(case_surface, (left_x, self.header_rect.top + 4))
        surface.blit(status_surface, (left_x, self.header_rect.top + 24))

    def _draw_board(self, surface: pygame.Surface) -> None:
        board_shadow = self.board_rect.move(0, 10)
        pygame.draw.rect(
            surface,
            _mix(COLOR_GAME_PANEL_BORDER, COLOR_GAME_BACKGROUND_SHADE, 0.55),
            board_shadow,
            border_radius=CONTAINER_RADIUS,
        )
        pygame.draw.rect(surface, COLOR_GAME_PANEL, self.board_rect, border_radius=CONTAINER_RADIUS)
        pygame.draw.rect(surface, COLOR_GAME_PANEL_BORDER, self.board_rect, width=1, border_radius=CONTAINER_RADIUS)

        for row_cells in self.cells:
            for cell in row_cells:
                cell.draw(surface, self.cell_font)

        self._draw_relations(surface)

    def draw(self, surface: pygame.Surface) -> None:
        self._update_layout()

        if self.force_full_draw:
            self._draw_background(surface)
            self._draw_header(surface)
            self._draw_board(surface)
            self.force_full_draw = False
            self.ai_dirty_cells.clear()
            return

        # In AI mode, keep background/board static and update only changed cells.
        if self.screen_mode == "ai" and (self.ai_animating or self.ai_solver_running):
            self._draw_header(surface)
            self._draw_incremental_board(surface)
            return

        self._draw_background(surface)
        self._draw_header(surface)
        self._draw_board(surface)
