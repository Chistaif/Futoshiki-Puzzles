"""Shared rendering helpers for the Futoshiki interface."""

from __future__ import annotations

from typing import Tuple

import pygame

from .constants import COLOR_BACKGROUND, COLOR_RELATION


def _mix(color_a: Tuple[int, int, int], color_b: Tuple[int, int, int], ratio: float) -> Tuple[int, int, int]:
    ratio = max(0.0, min(1.0, ratio))
    return (
        int(color_a[0] + (color_b[0] - color_a[0]) * ratio),
        int(color_a[1] + (color_b[1] - color_a[1]) * ratio),
        int(color_a[2] + (color_b[2] - color_a[2]) * ratio),
    )


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