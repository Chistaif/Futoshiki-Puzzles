"""Minimalist Japanese-style main menu."""

from __future__ import annotations

from typing import Any, Dict, Optional

import pygame

from ..components import Button
from ..constants import (
    BUTTON_HEIGHT,
    COLOR_BUTTON,
    COLOR_BUTTON_HOVER,
    COLOR_BUTTON_TEXT,
    FONT_BUTTON_SIZE,
    FONT_FAMILY,
)
from ..utils import _draw_soft_background

Transition = Optional[Dict[str, Any]]


class MenuScreen:
    """Minimal menu with Play, AI Solver, and Exit actions."""

    def __init__(self, surface_rect: pygame.Rect) -> None:
        self.surface_rect = surface_rect
        self.button_font = pygame.font.SysFont(FONT_FAMILY, FONT_BUTTON_SIZE - 2, bold=True)

        self.play_button = Button(
            pygame.Rect(0, 0, 248, BUTTON_HEIGHT),
            "Play",
            self.button_font,
            bg_color=COLOR_BUTTON,
            hover_color=COLOR_BUTTON_HOVER,
            text_color=COLOR_BUTTON_TEXT,
        )
        self.ai_button = Button(
            pygame.Rect(0, 0, 248, BUTTON_HEIGHT),
            "AI Solver",
            self.button_font,
            bg_color=COLOR_BUTTON,
            hover_color=COLOR_BUTTON_HOVER,
            text_color=COLOR_BUTTON_TEXT,
        )
        self.exit_button = Button(
            pygame.Rect(0, 0, 190, 50),
            "Exit",
            self.button_font,
            bg_color=COLOR_BUTTON,
            hover_color=COLOR_BUTTON_HOVER,
            text_color=COLOR_BUTTON_TEXT,
        )

        self._update_layout()

    def _update_layout(self) -> None:
        center_x = self.surface_rect.centerx
        play_center_y = self.surface_rect.centery + 84

        self.play_button.rect.center = (center_x, play_center_y)
        self.ai_button.rect.center = (center_x, play_center_y + BUTTON_HEIGHT + 18)
        self.exit_button.rect.center = (center_x, self.surface_rect.bottom - 52)

    def handle_event(self, event: pygame.event.Event) -> Transition:
        self._update_layout()

        if self.play_button.handle_event(event):
            return {"state": "deal_select", "mode": "play"}

        if self.ai_button.handle_event(event):
            return {"state": "deal_select", "mode": "ai"}

        if self.exit_button.handle_event(event):
            return {"state": "exit"}

        return None

    def update(self, _dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        self._update_layout()
        _draw_soft_background(surface)

        self.play_button.draw(surface)
        self.ai_button.draw(surface)
        self.exit_button.draw(surface)
