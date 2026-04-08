"""Level selection screen for choosing puzzle size."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import pygame

from ..components import Button
from ..constants import (
    COLOR_BACKGROUND,
    COLOR_BORDER,
    COLOR_ERROR,
    COLOR_MUTED,
    COLOR_PANEL,
    COLOR_SHADOW,
    COLOR_TITLE,
    FONT_BUTTON_SIZE,
    FONT_FAMILY,
    FONT_INFO_SIZE,
    FONT_SUBTITLE_SIZE,
    FONT_TITLE_SIZE,
    LEVEL_OPTIONS,
)
from ..utils import _draw_soft_background, _mix

Transition = Optional[Dict[str, Any]]


class LevelSelectScreen:
    """Screen where users choose board size before starting."""

    def __init__(self, surface_rect: pygame.Rect, available_sizes: Optional[Tuple[int, ...]] = None) -> None:
        self.surface_rect = surface_rect
        self.title_font = pygame.font.SysFont(FONT_FAMILY, FONT_TITLE_SIZE - 6, bold=True)
        self.subtitle_font = pygame.font.SysFont(FONT_FAMILY, FONT_SUBTITLE_SIZE)
        self.button_font = pygame.font.SysFont(FONT_FAMILY, FONT_BUTTON_SIZE - 2, bold=True)
        self.hint_font = pygame.font.SysFont(FONT_FAMILY, FONT_INFO_SIZE - 2)

        self.layout_margin = max(20, int(self.surface_rect.width * 0.04))
        self.header_top = self.layout_margin
        self.back_button = Button(pygame.Rect(0, 0, 132, 50), "Back", self.button_font)

        if available_sizes:
            self.level_options = tuple(sorted(available_sizes))
        else:
            self.level_options = LEVEL_OPTIONS

        self.level_buttons: List[Tuple[int, Button]] = []
        self._build_level_buttons()

    def _compute_grid_columns(self) -> int:
        if self.surface_rect.width < 760:
            return 2
        return 3

    def _compute_panel_rect(self, columns: int) -> pygame.Rect:
        row_count = max(1, (len(self.level_options) + columns - 1) // columns)
        spacing_x = 24
        spacing_y = 24
        button_width = 184 if columns == 2 else 176
        button_height = 82

        content_width = columns * button_width + (columns - 1) * spacing_x
        panel_width = min(self.surface_rect.width - self.layout_margin * 2, content_width + 80)
        panel_height = min(
            self.surface_rect.height - 230,
            row_count * button_height + max(0, row_count - 1) * spacing_y + 96,
        )

        panel_rect = pygame.Rect(0, 0, panel_width, panel_height)
        panel_rect.center = (self.surface_rect.centerx, self.surface_rect.centery + 44)
        return panel_rect

    def _build_level_buttons(self) -> None:
        self.level_buttons.clear()

        columns = self._compute_grid_columns()
        panel_rect = self._compute_panel_rect(columns)

        spacing_x = 24
        spacing_y = 24
        button_height = 82

        horizontal_space = panel_rect.width - 56 - (columns - 1) * spacing_x
        button_width = horizontal_space // columns
        start_x = panel_rect.left + (panel_rect.width - (columns * button_width + (columns - 1) * spacing_x)) // 2
        start_y = panel_rect.top + 46

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

        self.back_button.rect.topleft = (self.layout_margin, self.header_top)

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
        self._build_level_buttons()
        _draw_soft_background(surface)

        title = self.title_font.render("Select Level", True, COLOR_TITLE)
        subtitle = self.subtitle_font.render("Choose puzzle size from available inputs", True, COLOR_MUTED)

        title_y = self.header_top + 84
        surface.blit(title, title.get_rect(center=(self.surface_rect.centerx, title_y)))
        surface.blit(subtitle, subtitle.get_rect(center=(self.surface_rect.centerx, title_y + 44)))

        panel_rect = self._compute_panel_rect(self._compute_grid_columns())

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
