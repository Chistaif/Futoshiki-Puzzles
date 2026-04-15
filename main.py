"""Main entry point for the Futoshiki GUI."""

from __future__ import annotations

import pygame

from gui.constants import DEFAULT_GRID_SIZE, FPS, SCREEN_HEIGHT, SCREEN_WIDTH, WINDOW_TITLE
from gui.screens import DealSelectScreen, GameScreen, MenuScreen


def _compute_window_size_2_by_3() -> tuple[int, int]:
    """Return a window size that keeps a strict 2:3 (width:height) ratio and fits display."""
    display_info = pygame.display.Info()
    max_width = max(360, int(display_info.current_w * 0.94))
    max_height = max(540, int(display_info.current_h * 0.88))

    target_width = min(max_width, int(max_height * (2 / 3)))
    target_height = int(target_width * (3 / 2))

    if target_height > max_height:
        target_height = max_height
        target_width = int(target_height * (2 / 3))

    return target_width, target_height


def run() -> None:
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)

    default_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
    window_size = _compute_window_size_2_by_3()
    if window_size[0] <= 0 or window_size[1] <= 0:
        window_size = default_size

    surface = pygame.display.set_mode(window_size)
    clock = pygame.time.Clock()

    menu_screen = MenuScreen(surface.get_rect())
    game_screen = GameScreen(surface.get_rect(), n=DEFAULT_GRID_SIZE)
    deal_select_screen = DealSelectScreen(
        surface.get_rect(),
        available_sizes=game_screen.available_sizes,
        puzzles_by_size=game_screen.puzzles_by_size,
    )

    selected_level = game_screen.n
    state = "menu"
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0

        if state == "menu":
            active_screen = menu_screen
        elif state == "deal_select":
            active_screen = deal_select_screen
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

            if next_state == "exit":
                running = False
                continue

            if next_state == "deal_select":
                deal_select_screen.set_mode(str(transition.get("mode", "play")))

            if next_state == "game":
                selected_level = int(transition.get("level", selected_level))
                raw_case_name = transition.get("case_name")
                selected_case_name = raw_case_name.strip() if isinstance(raw_case_name, str) else None
                if selected_case_name == "":
                    selected_case_name = None

                game_screen.set_level(selected_level, selected_case_name)

                if bool(transition.get("start_ai", False)):
                    if game_screen.current_case is not None:
                        game_screen.start_ai_solver(game_screen.current_case, "backtracking")
                    else:
                        game_screen.status_message = "No puzzle available for AI solver"

            state = next_state

        active_screen.update(dt)
        active_screen.draw(surface)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run()