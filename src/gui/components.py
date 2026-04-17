"""Reusable visual components for the Futoshiki interface."""

from __future__ import annotations

import pygame

from .constants import (
    COLOR_AI_HIGHLIGHT,
    BUTTON_RADIUS,
    BUTTON_SHADOW_OFFSET,
    CELL_BORDER_WIDTH,
    CELL_RADIUS,
    COLOR_BACKGROUND,
    COLOR_BUTTON,
    COLOR_BUTTON_HOVER,
    COLOR_BUTTON_TEXT,
    COLOR_CLUE,
    COLOR_ERROR,
    COLOR_ERROR_SOFT,
    COLOR_GAME_ACCENT,
    COLOR_GAME_CELL,
    COLOR_GAME_CELL_BORDER,
    COLOR_GAME_CELL_SHADOW,
    COLOR_SHADOW,
    COLOR_SOLVER,
    COLOR_SOLVER_BACKTRACK,
)
from .utils import _mix


class Button:
    """Rounded button with soft shadow and hover effect."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        font: pygame.font.Font,
        bg_color: tuple[int, int, int] = COLOR_BUTTON,
        hover_color: tuple[int, int, int] = COLOR_BUTTON_HOVER,
        text_color: tuple[int, int, int] = COLOR_BUTTON_TEXT,
    ) -> None:
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)

        return False

    def draw(self, surface: pygame.Surface) -> None:
        shadow_rect = self.rect.move(0, BUTTON_SHADOW_OFFSET)
        pygame.draw.rect(
            surface,
            _mix(COLOR_SHADOW, COLOR_BACKGROUND, 0.15),
            shadow_rect,
            border_radius=BUTTON_RADIUS,
        )

        color = self.hover_color if self.is_hovered else self.bg_color
        pygame.draw.rect(surface, color, self.rect, border_radius=BUTTON_RADIUS)

        border_color = _mix(color, (0, 0, 0), 0.15)
        pygame.draw.rect(surface, border_color, self.rect, width=1, border_radius=BUTTON_RADIUS)

        label = self.font.render(self.text, True, self.text_color)
        label_rect = label.get_rect(center=self.rect.center)
        surface.blit(label, label_rect)


class Timer:
    """Simple in-game timer rendered as mm:ss."""

    def __init__(self) -> None:
        self.elapsed_seconds = 0.0
        self.running = False

    def start(self) -> None:
        self.elapsed_seconds = 0.0
        self.running = True

    def stop(self) -> None:
        self.running = False

    def update(self, dt: float) -> None:
        if self.running:
            self.elapsed_seconds += dt

    def format_time(self) -> str:
        total = int(self.elapsed_seconds)
        minutes = total // 60
        seconds = total % 60
        return f"{minutes:02d}:{seconds:02d}"

    def get_time(self) -> str:
        """Return formatted elapsed time for UI displays."""
        return self.format_time()


class Cell:
    """Grid cell with selected and invalid visual states."""

    def __init__(
        self,
        row: int,
        col: int,
        rect: pygame.Rect,
        value: int = 0,
        is_clue: bool = False,
    ) -> None:
        self.row = row
        self.col = col
        self.rect = pygame.Rect(rect)
        self.value = value
        self.is_clue = is_clue
        self.is_selected = False
        self.is_invalid = False
        self.is_ai_focus = False
        self.is_ai_backtrack = False

    def contains(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)

    def set_value(self, value: int) -> None:
        if not self.is_clue:
            self.value = value

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        shadow_rect = self.rect.move(0, 2)
        pygame.draw.rect(surface, COLOR_GAME_CELL_SHADOW, shadow_rect, border_radius=CELL_RADIUS)

        if self.is_invalid:
            fill = COLOR_ERROR_SOFT
        elif self.is_ai_focus:
            fill = _mix(COLOR_AI_HIGHLIGHT, COLOR_GAME_CELL, 0.45)
        else:
            fill = COLOR_GAME_CELL

        pygame.draw.rect(surface, fill, self.rect, border_radius=CELL_RADIUS)

        if self.is_invalid:
            border_color = COLOR_ERROR
        elif self.is_selected:
            border_color = COLOR_GAME_ACCENT
        elif self.is_ai_focus and self.is_ai_backtrack:
            border_color = COLOR_SOLVER_BACKTRACK
        elif self.is_ai_focus:
            border_color = COLOR_GAME_ACCENT
        else:
            border_color = COLOR_GAME_CELL_BORDER

        border_width = CELL_BORDER_WIDTH + 1 if (self.is_selected or self.is_ai_focus) else CELL_BORDER_WIDTH
        pygame.draw.rect(
            surface,
            border_color,
            self.rect,
            width=border_width,
            border_radius=CELL_RADIUS,
        )

        if self.value != 0:
            if self.is_clue:
                text_color = COLOR_CLUE
            elif self.is_ai_focus and self.is_ai_backtrack:
                text_color = COLOR_SOLVER_BACKTRACK
            else:
                text_color = COLOR_SOLVER
            text_surface = font.render(str(self.value), True, text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)

