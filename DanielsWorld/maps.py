import pygame
import sys
import os
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from settings import (
    WINDOW_SIZE, WINDOW_MODE, WINDOW_TITLE, FPS,
    PLAYER_SPEED, PLAYER_RADIUS, BACKGROUND_COLOR,
    PLAYER_PROJECTILE_COLOR, PLAYER_START_POS_RATIO,
    MOVEMENT_CONTROLS, WORLD1_MAP_PATH
)

# --- AI Dungeon Master ---
import importlib.util

class DungeonMaster:
    def __init__(self):
        self.intro_shown = False
        self.encounter_states = {}

    def narrate_intro(self, screen):
        if not self.intro_shown:
            self.show_message(screen, "Welcome, adventurer! I am your Dungeon Master. Explore the map and seek out encounters!")
            self.intro_shown = True

    def show_message(self, screen, text, duration=2.5):
        # Draw a semi-transparent box for dialogue
        box_width = int(screen.get_width() * 0.8)
        box_height = 90
        box_x = (screen.get_width() - box_width) // 2
        box_y = 30
        # Clear previous dialogue area
        if hasattr(self, 'last_box_rect') and self.last_box_rect:
            # Redraw background in the old box area
            if 'bg_image' in globals() and bg_image:
                bg_surf = pygame.transform.smoothscale(bg_image, (screen.get_width(), screen.get_height()))
                screen.blit(bg_surf, self.last_box_rect, self.last_box_rect)
            else:
                pygame.draw.rect(screen, BACKGROUND_COLOR if 'BACKGROUND_COLOR' in globals() else (0,0,0), self.last_box_rect)

        # Draw dialogue box
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(screen, (30, 30, 30, 220), box_rect, border_radius=16)
        pygame.draw.rect(screen, (255, 255, 0), box_rect, width=3, border_radius=16)

        # Render text (wrap if needed)
        font = pygame.font.SysFont(None, 32)
        lines = []
        words = text.split(' ')
        line = ''
        for word in words:
            test_line = line + word + ' '
            if font.size(test_line)[0] > box_width - 32:
                lines.append(line)
                line = word + ' '
            else:
                line = test_line
        lines.append(line)
        for i, l in enumerate(lines):
            msg = font.render(l.strip(), True, (255, 255, 0))
            msg_rect = msg.get_rect(midleft=(box_x + 20, box_y + 24 + i*32))
            screen.blit(msg, msg_rect)

        pygame.display.flip()
        self.last_box_rect = box_rect
        pygame.time.delay(int(duration * 1000))

    def encounter(self, screen, idx):
        if self.encounter_states.get(idx, False):
            return  # already completed
        self.show_message(screen, f"Encounter {idx+1}: A mysterious event! Press E to interact or move on.", duration=2)
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        self.show_message(screen, "You chose to enter the encounter!")
                        run_sebs_minigame(screen)
                        self.encounter_states[idx] = True
                        waiting = False
                        break
                    elif event.key in (pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d):
                        self.show_message(screen, "You chose to skip the encounter.")
                        self.encounter_states[idx] = True
                        waiting = False
                        break

# --- Minigame integration ---
def run_sebs_minigame(screen):
    # Dynamically import and run SebsMinigame.py
    minigame_path = project_root / "SebastiansAwesomeCode" / "SebsMinigame.py"
    spec = importlib.util.spec_from_file_location("SebsMinigame", str(minigame_path))
    sebs_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sebs_module)
    if hasattr(sebs_module, "main"):
        sebs_module.main()
    else:
        # fallback: rerun the file as script
        os.system(f"python {minigame_path}")

# --- Pygame setup ---
pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE if WINDOW_MODE == "RESIZABLE" else pygame.FULLSCREEN)
clock = pygame.time.Clock()
pygame.display.set_caption(WINDOW_TITLE)
running = True
dt = 0
bg_image = None
try:
    if WORLD1_MAP_PATH.exists():
        bg_image = pygame.image.load(str(WORLD1_MAP_PATH)).convert()
    else:
        print(f"Background image not found at {WORLD1_MAP_PATH}", file=sys.stderr)
except Exception as e:
    print(f"Failed to load background image: {e}", file=sys.stderr)
    bg_image = None

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

import random

# --- Encounter points and types ---
encounter_points = [
    {"pos": pygame.Vector2(screen.get_width() * 0.3, screen.get_height() * 0.4), "type": "dialogue", "character": "Mysterious Stranger"},
    {"pos": pygame.Vector2(screen.get_width() * 0.7, screen.get_height() * 0.6), "type": "minigame"},
    {"pos": pygame.Vector2(screen.get_width() * 0.5, screen.get_height() * 0.8), "type": "dialogue", "character": "Lost Robot"},
]

def ai_generate_dialogue(character):
    # Returns (prompt, [responses], [followups])
    if character == "Mysterious Stranger":
        prompt = "Greetings, traveler. The path ahead is perilous. Will you trust your instincts or seek guidance?"
        responses = [
            "I trust my instincts.",
            "I seek your guidance.",
            "Who are you?"
        ]
        followups = [
            "Stranger: Then may your instincts serve you well.",
            "Stranger: Very well. Beware the shadows ahead.",
            "Stranger: I am but a watcher in these lands."
        ]
    elif character == "Lost Robot":
        prompt = "Bzzt... Error! Where is my creator? Can you help me find my way?"
        responses = [
            "I'll help you!",
            "Sorry, I'm lost too.",
            "What do you remember?"
        ]
        followups = [
            "Robot: Thank you! Initializing gratitude protocol...",
            "Robot: Oh no! We are both lost. Bzzt...",
            "Robot: I remember... a warm light and a kind voice."
        ]
    else:
        prompt = "The wind whispers, but says nothing."
        responses = ["..."]
        followups = ["..."]
    return prompt, responses, followups

dm = DungeonMaster()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

    # draw background
    if bg_image:
        try:
            bg_surf = pygame.transform.smoothscale(bg_image, (screen.get_width(), screen.get_height()))
            screen.blit(bg_surf, (0, 0))
        except Exception:
            screen.blit(bg_image, (0, 0))
    else:
        screen.fill("black")

    # Draw player
    pygame.draw.circle(screen, "red", player_pos, 40)

    # Draw encounter points
    for idx, enc in enumerate(encounter_points):
        pt = enc["pos"]
        color = (0, 255, 255) if not dm.encounter_states.get(idx, False) else (100, 100, 100)
        pygame.draw.circle(screen, color, (int(pt.x), int(pt.y)), 30)

    # AI DM intro
    dm.narrate_intro(screen)

    # Check for encounter proximity
    for idx, enc in enumerate(encounter_points):
        pt = enc["pos"]
        if not dm.encounter_states.get(idx, False):
            if player_pos.distance_to(pt) < 60:
                if enc.get("type") == "dialogue":
                    # Dialogue event with character and player response
                    character = enc.get("character", "Stranger")
                    prompt, responses, followups = ai_generate_dialogue(character)
                    dm.show_message(screen, f"{character}: {prompt}", duration=2.5)
                    # Show response options
                    font = pygame.font.SysFont(None, 28)
                    box_width = int(screen.get_width() * 0.8)
                    box_x = (screen.get_width() - box_width) // 2
                    box_y = 130
                    box_height = 40 * len(responses) + 20
                    box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
                    pygame.draw.rect(screen, (40, 40, 40, 220), box_rect, border_radius=12)
                    pygame.draw.rect(screen, (255, 255, 0), box_rect, width=2, border_radius=12)
                    for i, resp in enumerate(responses):
                        msg = font.render(f"{i+1}. {resp}", True, (200, 255, 200))
                        msg_rect = msg.get_rect(midleft=(box_x + 24, box_y + 28 + i*36))
                        screen.blit(msg, msg_rect)
                    pygame.display.flip()
                    # Wait for player to press 1/2/3...
                    selected = None
                    while selected is None:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            elif event.type == pygame.KEYDOWN:
                                if pygame.K_1 <= event.key <= pygame.K_9:
                                    num = event.key - pygame.K_1
                                    if 0 <= num < len(responses):
                                        selected = num
                                        break
                    # Show followup
                    dm.show_message(screen, followups[selected], duration=2.5)
                    dm.encounter_states[idx] = True
                else:
                    # Minigame encounter as before
                    dm.encounter(screen, idx)

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_pos.y -= 300 * dt
    if keys[pygame.K_s]:
        player_pos.y += 300 * dt
    if keys[pygame.K_a]:
        player_pos.x -= 300 * dt
    if keys[pygame.K_d]:
        player_pos.x += 300 * dt

    pygame.display.flip()
    dt = clock.tick(60) / 1000

pygame.quit()