"""Shared rendering helpers for the Futoshiki interface."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import pygame

from .constants import COLOR_BACKGROUND, COLOR_RELATION, COLOR_STRIPE_END, COLOR_STRIPE_START

_MENU_BACKGROUND_CACHE: pygame.Surface | None = None


def _load_menu_background() -> pygame.Surface | None:
    global _MENU_BACKGROUND_CACHE
    if _MENU_BACKGROUND_CACHE is not None:
        return _MENU_BACKGROUND_CACHE

    file_path = Path(__file__).resolve()
    search_roots = [file_path.parents[1], *file_path.parents]
    candidate_parts = (("assets", "picture", "menu.png"), ("assets", "menu.png"))

    for root in search_roots:
        for parts in candidate_parts:
            candidate = root.joinpath(*parts)
            if candidate.exists():
                _MENU_BACKGROUND_CACHE = pygame.image.load(candidate.as_posix()).convert()
                return _MENU_BACKGROUND_CACHE

    _MENU_BACKGROUND_CACHE = None
    return None


def _mix(color_a: Tuple[int, int, int], color_b: Tuple[int, int, int], ratio: float) -> Tuple[int, int, int]:
    ratio = max(0.0, min(1.0, ratio))
    return (
        int(color_a[0] + (color_b[0] - color_a[0]) * ratio),
        int(color_a[1] + (color_b[1] - color_a[1]) * ratio),
        int(color_a[2] + (color_b[2] - color_a[2]) * ratio),
    )


def _draw_soft_background(surface: pygame.Surface) -> None:
    background = _load_menu_background()
    if background is not None:
        scaled = pygame.transform.smoothscale(background, surface.get_size())
        surface.blit(scaled, (0, 0))
        return

    surface.fill(COLOR_BACKGROUND)

    width, height = surface.get_size()
    if height <= 0:
        return

    # Subtle paper texture for minimalist look.
    for y in range(0, height, 2):
        ratio = y / max(1, height - 1)
        base = _mix(COLOR_STRIPE_START, COLOR_STRIPE_END, ratio)
        line_color = _mix(base, (255, 255, 255), 0.08 if (y // 4) % 2 == 0 else 0.02)
        pygame.draw.line(surface, line_color, (0, y), (width, y), 1)


def _draw_relation_symbol(
    surface: pygame.Surface,
    center: Tuple[int, int],
    symbol: str,
    size: int,
    stroke: int,
    color: Tuple[int, int, int] = COLOR_RELATION,
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

    if stroke <= 1:
        pygame.draw.aaline(surface, color, points[0], points[1])
        pygame.draw.aaline(surface, color, points[1], points[2])
        return

    pygame.draw.line(surface, color, points[0], points[1], stroke)
    pygame.draw.line(surface, color, points[1], points[2], stroke)
