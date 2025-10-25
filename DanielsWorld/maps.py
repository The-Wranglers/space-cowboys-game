import pygame
from pathlib import Path
import sys

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
clock = pygame.time.Clock()
pygame.display.set_caption("Space Cowboy")
running = True
dt = 0

# Attempt to load the world background image from the project assets
# This looks for the file at <repo root>/assets/images/World1Map.png
ASSET_PATH = Path(__file__).resolve().parents[1] / "assets" / "images" / "World1Map.png"
bg_image = None
try:
    if ASSET_PATH.exists():
        # use convert() or convert_alpha() depending on image transparency
        bg_image = pygame.image.load(str(ASSET_PATH)).convert()
    else:
        print(f"Background image not found at {ASSET_PATH}", file=sys.stderr)
except Exception as e:
    print(f"Failed to load background image: {e}", file=sys.stderr)
    bg_image = None

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

while running:
    # poll for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            # recreate the screen surface at the new size so get_width/height match
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

    # draw background (scaled to current window size)
    if bg_image:
        try:
            bg_surf = pygame.transform.smoothscale(bg_image, (screen.get_width(), screen.get_height()))
            screen.blit(bg_surf, (0, 0))
        except Exception:
            # fallback: blit original (may be smaller or larger than window)
            screen.blit(bg_image, (0, 0))
    else:
        # fallback background
        screen.fill("black")

    # RENDER YOUR GAME HERE
    pygame.draw.circle(screen, "red", player_pos, 40)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_pos.y -= 300 * dt
    if keys[pygame.K_s]:
        player_pos.y += 300 * dt
    if keys[pygame.K_a]:
        player_pos.x -= 300 * dt
    if keys[pygame.K_d]:
        player_pos.x += 300 * dt

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()