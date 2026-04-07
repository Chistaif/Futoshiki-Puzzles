"""Main entry point for the Futoshiki GUI."""

from __future__ import annotations

import pygame

from gui.constants import DEFAULT_GRID_SIZE, FPS, SCREEN_HEIGHT, SCREEN_WIDTH, WINDOW_TITLE
from gui.screens import GameScreen, LevelSelectScreen, MenuScreen


def run() -> None:
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)

    surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    menu_screen = MenuScreen(surface.get_rect())
    game_screen = GameScreen(surface.get_rect(), n=DEFAULT_GRID_SIZE)
    level_select_screen = LevelSelectScreen(surface.get_rect(), available_sizes=game_screen.available_sizes)

    selected_level = game_screen.n
    state = "menu"
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0

        if state == "menu":
            active_screen = menu_screen
        elif state == "level_select":
            active_screen = level_select_screen
        else:
            active_screen = game_screen

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            transition = active_screen.handle_event(event)
            if transition is None:
                continue

            next_state = transition.get("state", state)
            if next_state == "game":
                selected_level = int(transition.get("level", selected_level))
                game_screen.set_level(selected_level)

            state = next_state

        active_screen.update(dt)
        active_screen.draw(surface)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run()
