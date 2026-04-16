"""Deal and input selection screen."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pygame

from file import PuzzleCase

from ..components import Button
from ..constants import (
    COLOR_BUTTON,
    COLOR_BUTTON_HOVER,
    COLOR_BUTTON_TEXT,
    COLOR_MUTED,
    FONT_BUTTON_SIZE,
    FONT_FAMILY,
    FONT_INFO_SIZE,
    FONT_SUBTITLE_SIZE,
    FONT_TITLE_SIZE,
    LEVEL_OPTIONS,
)
from ..utils import _draw_soft_background, _mix

Transition = Optional[Dict[str, Any]]


class DealSelectScreen:
    """Two-step selector: choose deal size, then choose input file."""

    def __init__(
        self,
        surface_rect: pygame.Rect,
        available_sizes: Optional[Tuple[int, ...]] = None,
        puzzles_by_size: Optional[Dict[int, List[PuzzleCase]]] = None,
    ) -> None:
        self.surface_rect = surface_rect
        self.title_font = pygame.font.SysFont(FONT_FAMILY, FONT_TITLE_SIZE - 10, bold=True)
        self.subtitle_font = pygame.font.SysFont(FONT_FAMILY, FONT_SUBTITLE_SIZE - 2, bold=True)
        self.button_font = pygame.font.SysFont(FONT_FAMILY, FONT_BUTTON_SIZE - 4, bold=True)
        self.small_font = pygame.font.SysFont(FONT_FAMILY, FONT_INFO_SIZE - 1, bold=True)

        self.puzzles_by_size: Dict[int, List[PuzzleCase]] = {}
        if puzzles_by_size:
            for size, cases in puzzles_by_size.items():
                self.puzzles_by_size[size] = sorted(cases, key=lambda case: case.name.lower())

        size_set = set(self.puzzles_by_size.keys())
        if available_sizes:
            size_set.update(available_sizes)

        self.level_options = tuple(sorted(size_set)) if size_set else LEVEL_OPTIONS

        self.mode = "play"
        self.stage = "deal"
        self.layout_margin = max(16, int(self.surface_rect.width * 0.03))
        self.selected_size: Optional[int] = None
        self.hovered_size: Optional[int] = None
        self.hovered_case_name: Optional[str] = None
        self.deal_button_rects: List[Tuple[int, pygame.Rect]] = []
        self.input_button_rects: List[Tuple[str, pygame.Rect]] = []

        self.back_button = Button(
            pygame.Rect(0, 0, 88, 44),
            "",
            self.button_font,
            bg_color=COLOR_BUTTON,
            hover_color=COLOR_BUTTON_HOVER,
            text_color=COLOR_BUTTON_TEXT,
        )

        self.panel_rect = pygame.Rect(0, 0, 100, 100)
        self._update_layout()

    def set_mode(self, mode: str) -> None:
        self.mode = "ai" if str(mode).lower() == "ai" else "play"

    def _cases_for_selected_size(self) -> List[PuzzleCase]:
        if self.selected_size is None:
            return []
        return self.puzzles_by_size.get(self.selected_size, [])

    def _grid_columns(self, count: int) -> int:
        return 2 if count > 4 else 1

    def _compute_panel_height(self, option_count: int) -> int:
        count = max(1, option_count)
        cols = self._grid_columns(count)
        rows = (count + cols - 1) // cols
        button_height = 50
        spacing_y = 14
        content_height = rows * button_height + max(0, rows - 1) * spacing_y
        desired_height = 220 + content_height
        max_height = self.surface_rect.height - 120
        return max(390, min(max_height, desired_height))

    def _build_option_rects(self, count: int) -> List[pygame.Rect]:
        if count <= 0:
            return []

        cols = self._grid_columns(count)
        spacing_x = 16
        spacing_y = 14
        button_height = 50
        inner_width = self.panel_rect.width - 56
        button_width = (inner_width - spacing_x * (cols - 1)) // cols

        start_x = self.panel_rect.left + 28
        start_y = self.panel_rect.top + 130

        rects: List[pygame.Rect] = []
        for index in range(count):
            row = index // cols
            col = index % cols
            x = start_x + col * (button_width + spacing_x)
            y = start_y + row * (button_height + spacing_y)
            rects.append(pygame.Rect(x, y, button_width, button_height))

        return rects

    def _update_layout(self) -> None:
        self.layout_margin = max(16, int(self.surface_rect.width * 0.03))

        if self.selected_size is None and self.level_options:
            self.selected_size = self.level_options[0]

        if self.stage == "input" and self.selected_size not in self.level_options:
            self.stage = "deal"

        option_count = len(self.level_options)
        if self.stage == "input":
            option_count = len(self._cases_for_selected_size())

        panel_height = self._compute_panel_height(option_count)
        self.panel_rect = pygame.Rect(0, 0, min(560, self.surface_rect.width - 48), panel_height)
        self.panel_rect.center = (self.surface_rect.centerx, self.surface_rect.centery + 10)
        self.panel_rect.top = max(88, self.panel_rect.top)

        self.back_button.rect.topleft = (self.layout_margin, self.layout_margin)

        self.deal_button_rects = []
        self.input_button_rects = []

        if self.stage == "deal":
            rects = self._build_option_rects(len(self.level_options))
            self.deal_button_rects = list(zip(self.level_options, rects))
        else:
            case_names = [case.name for case in self._cases_for_selected_size()]
            rects = self._build_option_rects(len(case_names))
            self.input_button_rects = list(zip(case_names, rects))

    def _format_case_label(self, case_name: str) -> str:
        stem = Path(case_name).stem
        parts = stem.split("-", 1)
        if len(parts) == 2 and parts[0].lower() == "input" and parts[1].isdigit():
            return f"Input-{int(parts[1]):02d}"
        return stem

    def handle_event(self, event: pygame.event.Event) -> Transition:
        self._update_layout()

        if self.back_button.handle_event(event):
            if self.stage == "input":
                self.stage = "deal"
                self.hovered_case_name = None
                return None
            return {"state": "menu"}

        if event.type == pygame.MOUSEMOTION:
            if self.stage == "deal":
                self.hovered_size = None
                for size, rect in self.deal_button_rects:
                    if rect.collidepoint(event.pos):
                        self.hovered_size = size
                        break
            else:
                self.hovered_case_name = None
                for case_name, rect in self.input_button_rects:
                    if rect.collidepoint(event.pos):
                        self.hovered_case_name = case_name
                        break

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.stage == "deal":
                for size, rect in self.deal_button_rects:
                    if rect.collidepoint(event.pos):
                        self.selected_size = size
                        self.stage = "input"
                        self.hovered_case_name = None
                        return None
            else:
                for case_name, rect in self.input_button_rects:
                    if rect.collidepoint(event.pos) and self.selected_size is not None:
                        return {
                            "state": "game",
                            "level": self.selected_size,
                            "case_name": case_name,
                            "start_ai": self.mode == "ai",
                        }

        return None

    def update(self, _dt: float) -> None:
        pass

    def _draw_panel(self, surface: pygame.Surface) -> None:
        shadow = self.panel_rect.move(0, 6)
        pygame.draw.rect(surface, _mix((0, 0, 0), (16, 16, 16), 0.78), shadow, border_radius=20)
        pygame.draw.rect(surface, (16, 16, 16, 210), self.panel_rect, border_radius=20)
        pygame.draw.rect(surface, (230, 185, 60), self.panel_rect, width=1, border_radius=20)

    def _draw_title(self, surface: pygame.Surface) -> None:
        if self.stage == "deal":
            title_text = "SELECT DEAL"
            subtitle_text = "Choose board size"
        else:
            title_text = "SELECT INPUT"
            if self.selected_size is None:
                subtitle_text = "Choose puzzle"
            else:
                subtitle_text = f"Deal {self.selected_size}x{self.selected_size}"

        mode_text = "AI" if self.mode == "ai" else "PLAY"

        title = self.title_font.render(title_text, True, (246, 214, 95))
        subtitle = self.subtitle_font.render(subtitle_text, True, (246, 214, 95))
        mode = self.small_font.render(mode_text, True, COLOR_MUTED)

        surface.blit(title, title.get_rect(center=(self.surface_rect.centerx, self.panel_rect.top + 48)))
        surface.blit(subtitle, subtitle.get_rect(center=(self.surface_rect.centerx, self.panel_rect.top + 84)))
        surface.blit(mode, mode.get_rect(center=(self.surface_rect.centerx, self.panel_rect.top + 108)))

    def _draw_deal_buttons(self, surface: pygame.Surface) -> None:
        for size, rect in self.deal_button_rects:
            is_selected = size == self.selected_size
            is_hovered = size == self.hovered_size
            fill = (211, 102, 18) if is_selected or is_hovered else (34, 34, 34)

            pygame.draw.rect(surface, fill, rect, border_radius=9)
            pygame.draw.rect(surface, (230, 185, 60), rect, width=1, border_radius=9)

            label = self.button_font.render(f"Deal {size}x{size}", True, (255, 245, 210))
            surface.blit(label, label.get_rect(center=rect.center))

    def _draw_input_buttons(self, surface: pygame.Surface) -> None:
        if not self.input_button_rects:
            message = self.subtitle_font.render("No input file for this deal", True, COLOR_MUTED)
            surface.blit(message, message.get_rect(center=self.panel_rect.center))
            return

        for case_name, rect in self.input_button_rects:
            is_hovered = case_name == self.hovered_case_name
            fill = (211, 102, 18) if is_hovered else (34, 34, 34)

            pygame.draw.rect(surface, fill, rect, border_radius=9)
            pygame.draw.rect(surface, (230, 185, 60), rect, width=1, border_radius=9)

            label = self.button_font.render(self._format_case_label(case_name), True, (255, 245, 210))
            surface.blit(label, label.get_rect(center=rect.center))

    def draw(self, surface: pygame.Surface) -> None:
        self._update_layout()
        _draw_soft_background(surface)

        self._draw_panel(surface)
        self._draw_title(surface)

        if self.stage == "deal":
            self._draw_deal_buttons(surface)
        else:
            self._draw_input_buttons(surface)

        self.back_button.draw(surface)

        icon_color = (255, 248, 220) if self.back_button.is_hovered else COLOR_BUTTON_TEXT
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
