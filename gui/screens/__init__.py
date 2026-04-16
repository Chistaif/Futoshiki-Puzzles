"""Screen package exports for backward compatibility."""

from .deal_select import DealSelectScreen
from .game import GameScreen
from .level_select import LevelSelectScreen
from .menu import MenuScreen

__all__ = ["MenuScreen", "LevelSelectScreen", "DealSelectScreen", "GameScreen"]