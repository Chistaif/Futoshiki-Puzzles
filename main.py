"""Main entry point for the Futoshiki GUI."""

from __future__ import annotations

from pathlib import Path
import ctypes
import sys

import pygame

from src.gui.constants import DEFAULT_GRID_SIZE, FPS, SCREEN_HEIGHT, SCREEN_WIDTH, WINDOW_TITLE
from src.gui.screens import DealSelectScreen, GameScreen, MenuScreen


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


def _set_app_icon() -> None:
    """Set custom app icon if icon file exists and can be loaded."""
    icon_path = Path(__file__).resolve().parent / "assets" / "picture" / "icon_game.png"
    if not icon_path.exists():
        return

    try:
        icon_surface = pygame.image.load(icon_path.as_posix())
        icon_surface = _normalize_icon_surface(icon_surface, target_size=256)
        pygame.display.set_icon(icon_surface)
    except pygame.error:
        # Keep default icon when image format/loading is not supported.
        return


def _normalize_icon_surface(surface: pygame.Surface, target_size: int = 256) -> pygame.Surface:
    """Trim transparent padding and fit icon into a square canvas for better visibility."""
    bounds = surface.get_bounding_rect(min_alpha=1)
    if bounds.width > 0 and bounds.height > 0:
        content = surface.subsurface(bounds).copy()
    else:
        content = surface.copy()

    content_w, content_h = content.get_size()
    if content_w <= 0 or content_h <= 0:
        return surface

    scale = min(target_size / content_w, target_size / content_h)
    scaled_w = max(1, int(content_w * scale))
    scaled_h = max(1, int(content_h * scale))
    scaled = pygame.transform.smoothscale(content, (scaled_w, scaled_h))

    canvas = pygame.Surface((target_size, target_size), pygame.SRCALPHA)
    offset_x = (target_size - scaled_w) // 2
    offset_y = (target_size - scaled_h) // 2
    canvas.blit(scaled, (offset_x, offset_y))
    return canvas


def _set_windows_app_user_model_id() -> None:
    """Set a custom Windows AppUserModelID so taskbar can use app identity/icon."""
    if not sys.platform.startswith("win"):
        return

    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "futoshiki.puzzles.app"
        )
    except Exception:
        # Non-critical on unsupported environments.
        return


def run() -> None:
    _set_windows_app_user_model_id()
    pygame.init()
    _set_app_icon()
    pygame.display.set_caption(WINDOW_TITLE)

    default_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
    window_size = _compute_window_size_2_by_3()
    if window_size[0] <= 0 or window_size[1] <= 0:
        window_size = default_size

    surface = pygame.display.set_mode(window_size)
    _set_app_icon()
    clock = pygame.time.Clock()

    menu_screen = MenuScreen(surface.get_rect())
    game_screen = GameScreen(surface.get_rect(), n=DEFAULT_GRID_SIZE)
    deal_select_screen = DealSelectScreen(
        surface.get_rect(),
        available_sizes=game_screen.available_sizes,
        puzzles_by_size=game_screen.puzzles_by_size,
    )

    selected_level = game_screen.n
    selected_ai_solver = "backtracking"
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
                selected_ai_solver = str(transition.get("solver_name", selected_ai_solver))

            if next_state == "game":
                selected_level = int(transition.get("level", selected_level))
                raw_case_name = transition.get("case_name")
                selected_case_name = raw_case_name.strip() if isinstance(raw_case_name, str) else None
                if selected_case_name == "":
                    selected_case_name = None
                is_ai_mode = bool(transition.get("start_ai", False))
                game_screen.set_mode("ai" if is_ai_mode else "play")

                game_screen.set_level(selected_level, selected_case_name)

                if is_ai_mode:
                    if game_screen.current_case is not None:
                        game_screen.start_ai_solver(game_screen.current_case, selected_ai_solver)
                    else:
                        game_screen.status_message = "No puzzle available for AI solver"

            state = next_state

        active_screen.update(dt)
        active_screen.draw(surface)
        pygame.display.flip()

    game_screen.shutdown()
    pygame.quit()


if __name__ == "__main__":
    run()