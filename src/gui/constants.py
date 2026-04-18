"""Visual constants and layout presets for the Futoshiki GUI."""

from __future__ import annotations


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert #RRGGBB to an RGB tuple."""
    value = hex_color.strip().lstrip("#")
    if len(value) != 6:
        raise ValueError(f"Invalid HEX color: {hex_color}")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


WINDOW_TITLE = "Futoshiki - Classic Edition"
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 1080
FPS = 60

DEFAULT_GRID_SIZE = 4
LEVEL_OPTIONS = (4, 5, 6, 7, 8, 9)

# Classic FreeCell-inspired palette.
COLOR_BACKGROUND_HEX = "#076D1B"
COLOR_STRIPE_START_HEX = "#056416"
COLOR_STRIPE_END_HEX = "#057616"
COLOR_PANEL_HEX = "#046238"
COLOR_MENU_BAR_HEX = "#044F2E"
COLOR_STATUS_BAR_HEX = "#044F2E"

COLOR_CELL_HEX = "#FFFFFF"
COLOR_BORDER_HEX = "#A8AFB8"
COLOR_CLUE_HEX = "#121212"
COLOR_SOLVER_HEX = "#1D4FA3"
COLOR_SOLVER_BACKTRACK_HEX = "#7A1C1C"
COLOR_AI_HIGHLIGHT_HEX = "#FFF4AA"
COLOR_SELECTED_HEX = "#FFDF64"

COLOR_ERROR_HEX = "#BE1919"
COLOR_ERROR_SOFT_HEX = "#F8DADA"
COLOR_RELATION_HEX = "#FFFAD2"
COLOR_TITLE_HEX = "#FFF5A0"
COLOR_MUTED_HEX = "#F5F8D6"
COLOR_MENU_TEXT_HEX = "#FFFAD2"
COLOR_MENU_HOVER_HEX = "#D4AF37"
COLOR_BUTTON_HEX = "#800020"
COLOR_BUTTON_HOVER_HEX = "#A01234"
COLOR_BUTTON_TEXT_HEX = "#FFFAD2"
COLOR_SHADOW_HEX = "#022A15"
COLOR_SUCCESS_SOFT_HEX = "#0F3E28"
# Modern gameplay palette used by the redesigned game screen.
COLOR_GAME_BACKGROUND_HEX = "#F5F5F7"
COLOR_GAME_BACKGROUND_SHADE_HEX = "#EAEAEE"
COLOR_GAME_DARK_BACKGROUND_HEX = "#1A1A2E"
COLOR_GAME_PANEL_HEX = "#FFFFFF"
COLOR_GAME_PANEL_BORDER_HEX = "#D4D9E2"
COLOR_GAME_CELL_HEX = "#FFFFFF"
COLOR_GAME_CELL_BORDER_HEX = "#D1D6E0"
COLOR_GAME_CELL_SHADOW_HEX = "#C7CEDA"
COLOR_GAME_ACCENT_HEX = "#007AFF"
COLOR_GAME_TEXT_HEX = "#1E2430"
COLOR_GAME_MUTED_HEX = "#6B7385"
COLOR_RELATION_IDLE_HEX = "#8B93A5"
COLOR_RELATION_ACTIVE_HEX = "#FFB300"

COLOR_BACKGROUND = hex_to_rgb(COLOR_BACKGROUND_HEX)
COLOR_STRIPE_START = hex_to_rgb(COLOR_STRIPE_START_HEX)
COLOR_STRIPE_END = hex_to_rgb(COLOR_STRIPE_END_HEX)
COLOR_PANEL = hex_to_rgb(COLOR_PANEL_HEX)
COLOR_MENU_BAR = hex_to_rgb(COLOR_MENU_BAR_HEX)
COLOR_STATUS_BAR = hex_to_rgb(COLOR_STATUS_BAR_HEX)
COLOR_CELL = hex_to_rgb(COLOR_CELL_HEX)
COLOR_CLUE = hex_to_rgb(COLOR_CLUE_HEX)
COLOR_SOLVER = hex_to_rgb(COLOR_SOLVER_HEX)
COLOR_SOLVER_BACKTRACK = hex_to_rgb(COLOR_SOLVER_BACKTRACK_HEX)
COLOR_AI_HIGHLIGHT = hex_to_rgb(COLOR_AI_HIGHLIGHT_HEX)
COLOR_BORDER = hex_to_rgb(COLOR_BORDER_HEX)
COLOR_SELECTED = hex_to_rgb(COLOR_SELECTED_HEX)
COLOR_ERROR = hex_to_rgb(COLOR_ERROR_HEX)
COLOR_ERROR_SOFT = hex_to_rgb(COLOR_ERROR_SOFT_HEX)
COLOR_RELATION = hex_to_rgb(COLOR_RELATION_HEX)
COLOR_TITLE = hex_to_rgb(COLOR_TITLE_HEX)
COLOR_MUTED = hex_to_rgb(COLOR_MUTED_HEX)
COLOR_MENU_TEXT = hex_to_rgb(COLOR_MENU_TEXT_HEX)
COLOR_MENU_HOVER = hex_to_rgb(COLOR_MENU_HOVER_HEX)
COLOR_BUTTON = hex_to_rgb(COLOR_BUTTON_HEX)
COLOR_BUTTON_HOVER = hex_to_rgb(COLOR_BUTTON_HOVER_HEX)
COLOR_BUTTON_TEXT = hex_to_rgb(COLOR_BUTTON_TEXT_HEX)
COLOR_SHADOW = hex_to_rgb(COLOR_SHADOW_HEX)
COLOR_SUCCESS_SOFT = hex_to_rgb(COLOR_SUCCESS_SOFT_HEX)
COLOR_GAME_BACKGROUND = hex_to_rgb(COLOR_GAME_BACKGROUND_HEX)
COLOR_GAME_BACKGROUND_SHADE = hex_to_rgb(COLOR_GAME_BACKGROUND_SHADE_HEX)
COLOR_GAME_DARK_BACKGROUND = hex_to_rgb(COLOR_GAME_DARK_BACKGROUND_HEX)
COLOR_GAME_PANEL = hex_to_rgb(COLOR_GAME_PANEL_HEX)
COLOR_GAME_PANEL_BORDER = hex_to_rgb(COLOR_GAME_PANEL_BORDER_HEX)
COLOR_GAME_CELL = hex_to_rgb(COLOR_GAME_CELL_HEX)
COLOR_GAME_CELL_BORDER = hex_to_rgb(COLOR_GAME_CELL_BORDER_HEX)
COLOR_GAME_CELL_SHADOW = hex_to_rgb(COLOR_GAME_CELL_SHADOW_HEX)
COLOR_GAME_ACCENT = hex_to_rgb(COLOR_GAME_ACCENT_HEX)
COLOR_GAME_TEXT = hex_to_rgb(COLOR_GAME_TEXT_HEX)
COLOR_GAME_MUTED = hex_to_rgb(COLOR_GAME_MUTED_HEX)
COLOR_RELATION_IDLE = hex_to_rgb(COLOR_RELATION_IDLE_HEX)
COLOR_RELATION_ACTIVE = hex_to_rgb(COLOR_RELATION_ACTIVE_HEX)

FONT_FAMILY = "georgia"
FONT_SYMBOL = "segoeuisymbol"

FONT_TITLE_SIZE = 56
FONT_SUBTITLE_SIZE = 24
FONT_BUTTON_SIZE = 28
FONT_INFO_SIZE = 22

BUTTON_HEIGHT = 60
BUTTON_RADIUS = 16
BUTTON_SHADOW_OFFSET = 4

CELL_RADIUS = 8
CELL_BORDER_WIDTH = 1
CONTAINER_RADIUS = 28

# Path candidates: use assets/menu.png first, then fallback for existing repos.
MENU_IMAGE_CANDIDATES = (
    ("assets", "menu.png"),
    ("assets", "picture", "menu.png"),
)

# Grid presets by level (4x4 to 9x9).
GRID_CONFIG: dict[int, dict[str, int]] = {
    4: {
        "cell_size": 100,
        "gap": 26,
        "board_top": 150,
        "container_padding": 28,
        "cell_font": 50,
        "relation_size": 20,
        "relation_stroke": 2,
    },
    5: {
        "cell_size": 84,
        "gap": 20,
        "board_top": 144,
        "container_padding": 26,
        "cell_font": 43,
        "relation_size": 19,
        "relation_stroke": 2,
    },
    6: {
        "cell_size": 74,
        "gap": 18,
        "board_top": 138,
        "container_padding": 24,
        "cell_font": 38,
        "relation_size": 17,
        "relation_stroke": 2,
    },
    7: {
        "cell_size": 66,
        "gap": 15,
        "board_top": 134,
        "container_padding": 22,
        "cell_font": 34,
        "relation_size": 15,
        "relation_stroke": 2,
    },
    8: {
        "cell_size": 59,
        "gap": 13,
        "board_top": 130,
        "container_padding": 20,
        "cell_font": 31,
        "relation_size": 14,
        "relation_stroke": 2,
    },
    9: {
        "cell_size": 53,
        "gap": 11,
        "board_top": 124,
        "container_padding": 18,
        "cell_font": 28,
        "relation_size": 13,
        "relation_stroke": 2,
    },
}



