"""Menu screen for the Futoshiki interface."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import pygame

from ..components import Button
from ..constants import (
    BUTTON_HEIGHT,
    COLOR_MUTED,
    COLOR_TITLE,
    FONT_BUTTON_SIZE,
    FONT_FAMILY,
    FONT_SUBTITLE_SIZE,
    FONT_TITLE_SIZE,
    MENU_IMAGE_CANDIDATES,
)
from ..utils import _draw_soft_background

Transition = Optional[Dict[str, Any]]


def _load_menu_background() -> Optional[pygame.Surface]:
    root_path = Path(__file__).resolve().parents[2]
    for parts in MENU_IMAGE_CANDIDATES:
        candidate = root_path.joinpath(*parts)
        if candidate.exists():
            return pygame.image.load(candidate.as_posix()).convert()
    return None


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