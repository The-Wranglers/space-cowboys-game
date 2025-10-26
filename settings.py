"""
Space Cowboys Game Settings

This module contains all environmental variables and configuration settings for the Space Cowboys game.
Settings are organized by category for easy management and modification.
"""

from pathlib import Path

# Display Settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
WINDOW_MODE = "RESIZABLE"  # Can be "RESIZABLE" or "FULLSCREEN"
FPS = 60
WINDOW_TITLE = "Space Cowboy"

# Player Settings
PLAYER_SPEED = 300  # pixels per second
PLAYER_RADIUS = 40
PLAYER_START_POS_RATIO = (0.5, 0.5)  # ratio of screen width/height
PLAYER_COLOR = "blue"
PLAYER_FACE_COLOR = "black"

# Bullet Settings (from SebsMinigame)
BULLET_SPEED = 700  # pixels per second
BULLET_RADIUS = 15
BULLET_COLOR = "yellow"
BULLET_OFFSET = 40  # pixels from player center

# Asset Paths
BASE_PATH = Path(__file__).resolve().parent
ASSETS_PATH = BASE_PATH / "assets"
IMAGES_PATH = ASSETS_PATH / "images"
WORLD1_MAP_PATH = IMAGES_PATH / "World1Map.png"
LOGO_PATH = IMAGES_PATH / "logo.png"

# Colors
BACKGROUND_COLOR = "black"
PLAYER_PROJECTILE_COLOR = "red"

# Debug Settings
DEBUG_MODE = False  # Set to True to enable debug features
SHOW_FPS = False  # Show FPS counter when in debug mode

# Controls
MOVEMENT_CONTROLS = {
    "UP": "K_w",
    "DOWN": "K_s",
    "LEFT": "K_a",
    "RIGHT": "K_d",
    "SHOOT": "K_SPACE"
}

# Game Physics
PHYSICS_TIMESTEP = 1000  # milliseconds per physics update
