"""Menu screen for the Futoshiki interface."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import pygame

from ..constants import (
    BUTTON_HEIGHT,
    FONT_BUTTON_SIZE,
    FONT_FAMILY,
    MENU_IMAGE_CANDIDATES,
)
from ..utils import _draw_soft_background

Transition = Optional[Dict[str, Any]]

MENU_FRAME_RATIO = 2 / 3  # width / height
PLAY_BUTTON_WIDTH = 230
PLAY_BUTTON_RADIUS = 16

PLAY_BUTTON_BG = (255, 255, 255, 220)
PLAY_BUTTON_BG_HOVER = (242, 242, 242, 220)
PLAY_BUTTON_BORDER = (68, 68, 68, 120)
PLAY_BUTTON_TEXT = (30, 30, 30)


def _load_menu_background() -> Optional[pygame.Surface]:
    root_path = Path(__file__).resolve().parents[2]
    for parts in MENU_IMAGE_CANDIDATES:
        candidate = root_path.joinpath(*parts)
        if candidate.exists():
            return pygame.image.load(candidate.as_posix()).convert()
    return None


def _compute_menu_frame(surface_rect: pygame.Rect) -> pygame.Rect:
    """Build a centered portrait frame with a 2:3 ratio."""
    available_width = max(120, surface_rect.width)
    available_height = max(180, surface_rect.height)

    frame_width = min(available_width, int(available_height * MENU_FRAME_RATIO))
    frame_height = int(frame_width / MENU_FRAME_RATIO)

    frame = pygame.Rect(0, 0, frame_width, frame_height)
    frame.center = surface_rect.center
    return frame


def _scale_contain(source: pygame.Surface, target_rect: pygame.Rect) -> tuple[pygame.Surface, pygame.Rect]:
    """Scale image to fit inside target rect without cropping any details."""
    src_width, src_height = source.get_size()
    if src_width <= 0 or src_height <= 0:
        return source, source.get_rect(center=target_rect.center)

    ratio = min(target_rect.width / src_width, target_rect.height / src_height)
    scaled_width = max(1, int(src_width * ratio))
    scaled_height = max(1, int(src_height * ratio))
    scaled = pygame.transform.smoothscale(source, (scaled_width, scaled_height))
    scaled_rect = scaled.get_rect(center=target_rect.center)
    return scaled, scaled_rect


class MenuScreen:
    """Landing screen with hero background and Play CTA."""

    def __init__(self, surface_rect: pygame.Rect) -> None:
        self.surface_rect = surface_rect
        self.background_image = _load_menu_background()
        self.button_font = pygame.font.SysFont(FONT_FAMILY, FONT_BUTTON_SIZE, bold=True)
        self.play_button_rect = pygame.Rect(0, 0, PLAY_BUTTON_WIDTH, BUTTON_HEIGHT)
        self.is_play_hovered = False
        self._center_play_button()

    def _center_play_button(self) -> None:
        self.play_button_rect.center = self.surface_rect.center

    def _draw_play_button(self, surface: pygame.Surface) -> None:
        button_layer = pygame.Surface(self.play_button_rect.size, pygame.SRCALPHA)
        bg_color = PLAY_BUTTON_BG_HOVER if self.is_play_hovered else PLAY_BUTTON_BG
        pygame.draw.rect(button_layer, bg_color, button_layer.get_rect(), border_radius=PLAY_BUTTON_RADIUS)
        pygame.draw.rect(
            button_layer,
            PLAY_BUTTON_BORDER,
            button_layer.get_rect(),
            width=1,
            border_radius=PLAY_BUTTON_RADIUS,
        )
        surface.blit(button_layer, self.play_button_rect.topleft)

        label = self.button_font.render("Play", True, PLAY_BUTTON_TEXT)
        label_rect = label.get_rect(center=self.play_button_rect.center)
        surface.blit(label, label_rect)

    def handle_event(self, event: pygame.event.Event) -> Transition:
        if event.type == pygame.MOUSEMOTION:
            self.is_play_hovered = self.play_button_rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.play_button_rect.collidepoint(event.pos):
            return {"state": "level_select"}
        return None

    def update(self, _dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        self._center_play_button()
        _draw_soft_background(surface)

        menu_frame = _compute_menu_frame(self.surface_rect)
        if self.background_image is not None:
            image, image_rect = _scale_contain(self.background_image, menu_frame)
            surface.blit(image, image_rect)

        self._draw_play_button(surface)