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
        self.small_font = pygame.font.SysFont(FONT_FAMILY, FONT_BUTTON_SIZE - 8, bold=True)

        self.selected_ai_solver = "backtracking"
        self.solver_options = ("backtracking", "brute_force", "backward", "forward", "astar", "sat")
        self.solver_dropdown_open = False
        self.hovered_solver: Optional[str] = None
        self.solver_option_rects: list[tuple[str, pygame.Rect]] = []
        self.dropdown_anim_progress = 0.0
        self.dropdown_anim_duration = 0.16

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
        play_center_y = self.surface_rect.centery - 160

        self.play_button.rect.center = (center_x, play_center_y)
        self.ai_button.rect.center = (center_x, play_center_y + BUTTON_HEIGHT + 18)
        self.exit_button.rect.center = (center_x, self.surface_rect.bottom - 52)

        self.solver_option_rects = []
        for index, solver_name in enumerate(self.solver_options):
            rect = pygame.Rect(
                self.ai_button.rect.left,
                self.ai_button.rect.bottom + 10 + index * (BUTTON_HEIGHT - 8),
                self.ai_button.rect.width,
                BUTTON_HEIGHT - 12,
            )
            self.solver_option_rects.append((solver_name, rect))

    @staticmethod
    def _format_solver_label(solver_name: str) -> str:
        if solver_name == "brute_force":
            return "Brute Force"
        if solver_name == "backward":
            return "Backward Chaining"
        if solver_name == "forward":
            return "Forward Chaining"
        if solver_name == "astar":
            return "A* Search"
        if solver_name == "sat":
            return "SAT Solver"
        return "Backtracking"

    @staticmethod
    def _ease_out_cubic(value: float) -> float:
        clamped = max(0.0, min(1.0, value))
        return 1.0 - (1.0 - clamped) ** 3

    @staticmethod
    def _blend_rgba(color: tuple[int, int, int], alpha: int) -> tuple[int, int, int, int]:
        return color[0], color[1], color[2], max(0, min(255, alpha))

    def handle_event(self, event: pygame.event.Event) -> Transition:
        self._update_layout()

        if event.type == pygame.MOUSEMOTION and self.solver_dropdown_open:
            self.hovered_solver = None
            for solver_name, rect in self.solver_option_rects:
                if rect.collidepoint(event.pos):
                    self.hovered_solver = solver_name
                    break

        if self.play_button.handle_event(event):
            self.solver_dropdown_open = False
            return {"state": "deal_select", "mode": "play"}

        if self.ai_button.handle_event(event):
            self.solver_dropdown_open = not self.solver_dropdown_open
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.solver_dropdown_open:
            for solver_name, rect in self.solver_option_rects:
                if rect.collidepoint(event.pos):
                    self.selected_ai_solver = solver_name
                    self.solver_dropdown_open = False
                    return {
                        "state": "deal_select",
                        "mode": "ai",
                        "solver_name": self.selected_ai_solver,
                    }

            self.solver_dropdown_open = False

        if self.exit_button.handle_event(event):
            return {"state": "exit"}

        return None

    def update(self, dt: float) -> None:
        if self.dropdown_anim_duration <= 0:
            self.dropdown_anim_progress = 1.0 if self.solver_dropdown_open else 0.0
            return

        delta = dt / self.dropdown_anim_duration
        if self.solver_dropdown_open:
            self.dropdown_anim_progress = min(1.0, self.dropdown_anim_progress + delta)
        else:
            self.dropdown_anim_progress = max(0.0, self.dropdown_anim_progress - delta)

    def draw(self, surface: pygame.Surface) -> None:
        self._update_layout()
        _draw_soft_background(surface)

        self.play_button.draw(surface)
        self.ai_button.draw(surface)

        if self.dropdown_anim_progress > 0.0:
            for index, (solver_name, rect) in enumerate(self.solver_option_rects):
                stagger = index * 0.12
                if self.dropdown_anim_progress <= stagger:
                    continue

                local_progress = (self.dropdown_anim_progress - stagger) / (1.0 - stagger)
                eased = self._ease_out_cubic(local_progress)
                alpha = int(255 * eased)
                slide_y = int((1.0 - eased) * 16)

                animated_rect = rect.move(0, slide_y)
                option_surface = pygame.Surface((animated_rect.width, animated_rect.height), pygame.SRCALPHA)

                is_selected = solver_name == self.selected_ai_solver
                is_hovered = solver_name == self.hovered_solver
                fill = COLOR_BUTTON_HOVER if is_selected or is_hovered else COLOR_BUTTON

                pygame.draw.rect(
                    option_surface,
                    self._blend_rgba(fill, alpha),
                    option_surface.get_rect(),
                    border_radius=10,
                )
                pygame.draw.rect(
                    option_surface,
                    self._blend_rgba(COLOR_BUTTON_TEXT, alpha),
                    option_surface.get_rect(),
                    width=1,
                    border_radius=10,
                )

                label = self._format_solver_label(solver_name)
                label_surface = self.small_font.render(label, True, COLOR_BUTTON_TEXT)
                label_surface.set_alpha(alpha)
                option_surface.blit(label_surface, label_surface.get_rect(center=option_surface.get_rect().center))

                surface.blit(option_surface, animated_rect.topleft)

        self.exit_button.draw(surface)

