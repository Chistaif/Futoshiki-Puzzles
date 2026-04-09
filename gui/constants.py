"""Visual constants and layout presets for the Futoshiki GUI."""

from __future__ import annotations


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert #RRGGBB to an RGB tuple."""
    value = hex_color.strip().lstrip("#")
    if len(value) != 6:
        raise ValueError(f"Invalid HEX color: {hex_color}")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


WINDOW_TITLE = "Futoshiki - Modern UI"
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 780
FPS = 60

DEFAULT_GRID_SIZE = 4
LEVEL_OPTIONS = (4, 5, 6, 7, 8, 9)

# Palette required by the specification.
COLOR_BACKGROUND_HEX = "#F0F2F5"
COLOR_CELL_HEX = "#FFFFFF"
COLOR_CLUE_HEX = "#2C3E50"
COLOR_SOLVER_HEX = "#27AE60"

# Supporting colors for a premium flat style.
COLOR_PANEL_HEX = "#FAFBFD"
COLOR_BORDER_HEX = "#D8DEE8"
COLOR_SELECTED_HEX = "#D7E8FF"
COLOR_ERROR_HEX = "#E74C3C"
COLOR_ERROR_SOFT_HEX = "#FDEDEC"
COLOR_RELATION_HEX = "#34495E"
COLOR_TITLE_HEX = "#1F2D3D"
COLOR_MUTED_HEX = "#6C7A89"
COLOR_BUTTON_HEX = "#2F80ED"
COLOR_BUTTON_HOVER_HEX = "#1366D6"
COLOR_BUTTON_TEXT_HEX = "#FFFFFF"
COLOR_SHADOW_HEX = "#AAB4C0"
COLOR_SUCCESS_SOFT_HEX = "#E9F8EF"

COLOR_BACKGROUND = hex_to_rgb(COLOR_BACKGROUND_HEX)
COLOR_PANEL = hex_to_rgb(COLOR_PANEL_HEX)
COLOR_CELL = hex_to_rgb(COLOR_CELL_HEX)
COLOR_CLUE = hex_to_rgb(COLOR_CLUE_HEX)
COLOR_SOLVER = hex_to_rgb(COLOR_SOLVER_HEX)
COLOR_BORDER = hex_to_rgb(COLOR_BORDER_HEX)
COLOR_SELECTED = hex_to_rgb(COLOR_SELECTED_HEX)
COLOR_ERROR = hex_to_rgb(COLOR_ERROR_HEX)
COLOR_ERROR_SOFT = hex_to_rgb(COLOR_ERROR_SOFT_HEX)
COLOR_RELATION = hex_to_rgb(COLOR_RELATION_HEX)
COLOR_TITLE = hex_to_rgb(COLOR_TITLE_HEX)
COLOR_MUTED = hex_to_rgb(COLOR_MUTED_HEX)
COLOR_BUTTON = hex_to_rgb(COLOR_BUTTON_HEX)
COLOR_BUTTON_HOVER = hex_to_rgb(COLOR_BUTTON_HOVER_HEX)
COLOR_BUTTON_TEXT = hex_to_rgb(COLOR_BUTTON_TEXT_HEX)
COLOR_SHADOW = hex_to_rgb(COLOR_SHADOW_HEX)
COLOR_SUCCESS_SOFT = hex_to_rgb(COLOR_SUCCESS_SOFT_HEX)

FONT_FAMILY = "segoeui"
FONT_SYMBOL = "segoeuisymbol"

FONT_TITLE_SIZE = 56
FONT_SUBTITLE_SIZE = 24
FONT_BUTTON_SIZE = 28
FONT_INFO_SIZE = 22

BUTTON_HEIGHT = 60
BUTTON_RADIUS = 16
BUTTON_SHADOW_OFFSET = 6

CELL_RADIUS = 12
CELL_BORDER_WIDTH = 2
CONTAINER_RADIUS = 28

# Path candidates: use assets/menu.png first, then fallback for existing repos.
MENU_IMAGE_CANDIDATES = (
    ("assets", "menu.png"),
    ("assets", "picture", "menu.png"),
)

# Grid presets by level (4x4 to 9x9).
GRID_CONFIG: dict[int, dict[str, int]] = {
    4: {
        "cell_size": 90,
        "gap": 24,
        "board_top": 150,
        "container_padding": 30,
        "cell_font": 44,
        "relation_size": 22,
        "relation_stroke": 4,
    },
    5: {
        "cell_size": 75,
        "gap": 20,
        "board_top": 144,
        "container_padding": 26,
        "cell_font": 36,
        "relation_size": 20,
        "relation_stroke": 4,
    },
    6: {
        "cell_size": 65,
        "gap": 16,
        "board_top": 138,
        "container_padding": 24,
        "cell_font": 32,
        "relation_size": 18,
        "relation_stroke": 3,
    },
    7: {
        "cell_size": 55,
        "gap": 14,
        "board_top": 134,
        "container_padding": 22,
        "cell_font": 28,
        "relation_size": 16,
        "relation_stroke": 3,
    },
    8: {
        "cell_size": 48,
        "gap": 12,
        "board_top": 130,
        "container_padding": 20,
        "cell_font": 24,
        "relation_size": 14,
        "relation_stroke": 3,
    },
    9: {
        "cell_size": 42,
        "gap": 10,
        "board_top": 124,
        "container_padding": 18,
        "cell_font": 22,
        "relation_size": 12,
        "relation_stroke": 2,
    },
}

