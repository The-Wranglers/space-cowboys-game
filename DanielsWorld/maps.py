import pygame
import sys
import os
import random
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
from player_profile import PlayerProfile

# --- AI Dungeon Master ---
import importlib.util
import threading
import http.server
import socketserver
import json
import webbrowser

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

def run_presleyworld_minigame():
    # Run PresleyWorld/test.py as a subprocess
    presley_path = project_root / "PresleyWorld" / "test.py"
    os.system(f"python {presley_path}")

def start_pairing(profile):
    # choose a free port by binding a temporary socket
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    token = os.urandom(8).hex()
    
    class PairHandler(http.server.BaseHTTPRequestHandler):
        server_token = token
        
        def _set_cors(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        def do_OPTIONS(self):
            self.send_response(200)
            self._set_cors()
            self.end_headers()
        
        def do_POST(self):
            if self.path != '/pair':
                self.send_response(404)
                self.end_headers()
                return
            length = int(self.headers.get('Content-Length', 0))
            raw = self.rfile.read(length).decode('utf-8')
            try:
                data = json.loads(raw)
                if data.get('token') != self.server_token:
                    self.send_response(403)
                    self._set_cors()
                    self.end_headers()
                    return
                profile_data = data.get('profile')
                # Save linked account to player profile
                try:
                    profile.set_account(profile_data)
                except Exception:
                    pass
                self.send_response(200)
                self._set_cors()
                self.end_headers()
                # stop server after handling
                def stop_server():
                    httpd.shutdown()
                threading.Thread(target=stop_server, daemon=True).start()
            except Exception:
                self.send_response(400)
                self._set_cors()
                self.end_headers()

    # start server
    httpd = socketserver.TCPServer(("127.0.0.1", port), PairHandler)
    # open browser to the pairing page on the web server (assumes Web/ served at :8000)
    pair_url = f"http://localhost:8000/pair.html?token={token}&port={port}"
    try:
        webbrowser.open(pair_url)
    except Exception:
        pass
    # serve until pairing completes or timeout
    try:
        httpd.serve_forever()
    except Exception:
        pass

def draw_menu(screen, menu_options, menu_selection):
    # Draw darkened background
    dark_overlay = pygame.Surface((screen.get_width(), screen.get_height()))
    dark_overlay.fill((0, 0, 0))
    dark_overlay.set_alpha(128)
    screen.blit(dark_overlay, (0, 0))

    # Draw menu
    menu_font = pygame.font.SysFont(None, 36)
    menu_title = menu_font.render("Menu", True, (255, 255, 0))
    title_rect = menu_title.get_rect(centerx=screen.get_width() // 2, top=screen.get_height() // 3)
    screen.blit(menu_title, title_rect)

    for i, option in enumerate(menu_options):
        color = (255, 255, 0) if i == menu_selection else (200, 200, 200)
        text = menu_font.render(option, True, color)
        text_rect = text.get_rect(centerx=screen.get_width() // 2, 
                                top=title_rect.bottom + 40 + i * 40)
        if i == menu_selection:
            pygame.draw.rect(screen, color, text_rect.inflate(20, 5), 1)
        screen.blit(text, text_rect)

def ai_generate_dialogue(character):
    # Returns a dialogue structure: { prompt: str, options: [ {text, followup, loop} ] }
    if character == "Mysterious Stranger":
        return {
            "prompt": "Greetings, traveler. The path ahead is perilous. Will you trust your instincts or seek guidance?",
            "options": [
                {"text": "I trust my instincts.", "followup": "Stranger: Then may your instincts serve you well.", "loop": False},
                {"text": "I seek your guidance.", "followup": "Stranger: Very well. Beware the shadows ahead.", "loop": False, "effect": {"path_open": True}},
                {"text": "Who are you?", "followup": "Stranger: I am but a watcher in these lands.", "loop": True}
            ]
        }
    elif character == "Lost Robot":
        return {
            "prompt": "Bzzt... Error! Where is my creator? Can you help me find my way?",
            "options": [
                {"text": "I'll help you!", "followup": "Robot: Thank you! Initializing gratitude protocol...", "loop": False, "effect": {"robot_helped": True}},
                {"text": "Sorry, I'm lost too.", "followup": "Robot: Oh no! We are both lost. Bzzt...", "loop": False},
                {"text": "What do you remember?", "followup": "Robot: I remember... a warm light and a kind voice.", "loop": True}
            ]
        }
    elif character == "Gatekeeper":
        return {
            "prompt": "Halt! This path requires a token. Do you offer tribute or riddles?",
            "options": [
                {"text": "I offer tribute.", "followup": "Gatekeeper: The gate acknowledges your offering.", "loop": False, "effect": {"gate_unlocked": True}},
                {"text": "I will solve your riddle.", "followup": "Gatekeeper: Very well. What walks on four legs in the morning?", "loop": True}
            ]
        }
    else:
        return {"prompt": "The wind whispers, but says nothing.", "options": [{"text": "...", "followup": "...", "loop": False}]}

def handle_encounter(screen, dm, profile, encounter, idx):
    if encounter.get("type") == "dialogue":
        # Dialogue event with character and player response
        character = encounter.get("character", "Stranger")
        dialogue = ai_generate_dialogue(character)
        prompt = dialogue["prompt"]
        options = dialogue["options"]
        loop_count = 0
        max_loops = 3
        keep_looping = True
        while keep_looping and loop_count < max_loops:
            dm.show_message(screen, f"{character}: {prompt}", duration=1.0)
            # Show response options with visual selection
            font = pygame.font.SysFont(None, 28)
            box_width = int(screen.get_width() * 0.8)
            box_x = (screen.get_width() - box_width) // 2
            box_y = 130
            box_height = 48 * len(options) + 20
            box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
            # Draw box background
            s = pygame.Surface((box_rect.w, box_rect.h), pygame.SRCALPHA)
            s.fill((40, 40, 40, 220))
            screen.blit(s, (box_rect.x, box_rect.y))
            pygame.draw.rect(screen, (255, 255, 0), box_rect, width=2, border_radius=12)

            # selection state
            current_sel = 0
            # initialize selection from profile if present
            persisted = profile.get_choice(idx)
            if persisted is not None:
                try:
                    current_sel = int(persisted.get('selected', 0))
                except Exception:
                    current_sel = 0

            # draw options initially
            def render_options(highlight):
                for i, opt in enumerate(options):
                    y = box_y + 16 + i*48
                    opt_rect = pygame.Rect(box_x + 12, y, box_width - 24, 40)
                    if i == highlight:
                        pygame.draw.rect(screen, (60, 90, 60, 180), opt_rect, border_radius=8)
                    msg = font.render(f"{i+1}. {opt['text']}", True, (220, 255, 220) if i == highlight else (180, 220, 180))
                    screen.blit(msg, (box_x + 28, y + 8))
                # instructions
                instr = font.render("Use ↑/↓ to move, Enter to choose, or press number key", True, (200,200,200))
                screen.blit(instr, (box_x + 20, box_y + box_rect.h - 28))
                pygame.display.flip()

            render_options(current_sel)

            # Wait for player choice with visual highlight
            selected = None
            while selected is None:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            current_sel = (current_sel - 1) % len(options)
                            # redraw
                            if 'bg_image' in globals() and bg_image:
                                bg_surf = pygame.transform.smoothscale(bg_image, (screen.get_width(), screen.get_height()))
                                screen.blit(bg_surf, box_rect, box_rect)
                            else:
                                pygame.draw.rect(screen, (0,0,0), box_rect)
                            pygame.draw.rect(screen, (255,255,0), box_rect, width=2, border_radius=12)
                            render_options(current_sel)
                        elif event.key == pygame.K_DOWN:
                            current_sel = (current_sel + 1) % len(options)
                            if 'bg_image' in globals() and bg_image:
                                bg_surf = pygame.transform.smoothscale(bg_image, (screen.get_width(), screen.get_height()))
                                screen.blit(bg_surf, box_rect, box_rect)
                            else:
                                pygame.draw.rect(screen, (0,0,0), box_rect)
                            pygame.draw.rect(screen, (255,255,0), box_rect, width=2, border_radius=12)
                            render_options(current_sel)
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                            selected = current_sel
                            break
                        elif pygame.K_1 <= event.key <= pygame.K_9:
                            num = event.key - pygame.K_1
                            if 0 <= num < len(options):
                                selected = num
                                break

            # Show followup
            followup = options[selected].get('followup', '')
            # If the selected option or followup mentions riddle or puzzle, launch PresleyWorld minigame
            option_text = options[selected].get('text', '').lower()
            followup_text = followup.lower()
            if ("riddle" in option_text or "puzzle" in option_text or "riddle" in followup_text or "puzzle" in followup_text):
                dm.show_message(screen, "A mysterious puzzle awaits you...", duration=1.4)
                run_presleyworld_minigame()
            else:
                dm.show_message(screen, followup, duration=1.4)
            
            # persist choice into profile and apply any effects
            try:
                profile.set_choice(idx, selected, options[selected].get('text', ''))
                eff = options[selected].get('effect')
                if isinstance(eff, dict):
                    for kf, vf in eff.items():
                        profile.set_flag(kf, vf)
                    # if path opened by choice, dynamically add path encounter
                    if eff.get('path_open'):
                        if not any(enc.get('id') == 'path' for enc in encounter_points):
                            encounter_points.append({
                                "id": "path",
                                "pos": pygame.Vector2(screen.get_width() * 0.85, screen.get_height() * 0.3),
                                "type": "dialogue",
                                "character": "Gatekeeper"
                            })
            except Exception:
                pass
            # Decide whether to loop
            if options[selected].get('loop', False):
                prompt = followup
                loop_count += 1
                keep_looping = True
            else:
                keep_looping = False
        dm.encounter_states[idx] = True
    else:
        # Minigame encounter
        dm.encounter(screen, idx)

def main():
    # --- Pygame setup ---
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE if WINDOW_MODE == "RESIZABLE" else pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    pygame.display.set_caption(WINDOW_TITLE)

    # Load background image
    bg_image = None
    try:
        if WORLD1_MAP_PATH.exists():
            bg_image = pygame.image.load(str(WORLD1_MAP_PATH)).convert()
        else:
            print(f"Background image not found at {WORLD1_MAP_PATH}", file=sys.stderr)
    except Exception as e:
        print(f"Failed to load background image: {e}", file=sys.stderr)

    # Load player character images
    player_images = {}
    for direction in ['w', 'a', 's', 'd']:
        try:
            img_path = project_root / "assets" / "images" / f"{direction}Capy.png"
            player_images[direction] = pygame.image.load(str(img_path))
        except Exception as e:
            print(f"Failed to load player image {direction}Capy.png: {e}", file=sys.stderr)

    # Default player image (facing left)
    current_player_image = player_images.get('a')  # aCapy.png is the default
    if not current_player_image:  # Fallback if image loading failed
        print("Failed to load default player image, using placeholder", file=sys.stderr)
        current_player_image = pygame.Surface((80, 80))  # Create a placeholder surface
        current_player_image.fill("red")

    # Initialize player
    player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
    player_rect = current_player_image.get_rect(center=player_pos)

    # Load profile and initialize DM
    profile = PlayerProfile()
    dm = DungeonMaster()

    # Initialize menu state
    menu_active = False
    menu_selection = 0
    menu_options = ["Continue", "Reset Progress", "Link Online Account", "Back to Main Menu"]

    # Initialize encounter points
    encounter_points = [
        {"id": "enc0", "pos": pygame.Vector2(screen.get_width() * 0.3, screen.get_height() * 0.4), "type": "dialogue", "character": "Mysterious Stranger"},
        {"id": "enc1", "pos": pygame.Vector2(screen.get_width() * 0.7, screen.get_height() * 0.6), "type": "minigame"},
        {"id": "enc2", "pos": pygame.Vector2(screen.get_width() * 0.5, screen.get_height() * 0.8), "type": "dialogue", "character": "Lost Robot"},
    ]

    # Load profile choices and mark encounters done if present
    for k in profile.choices().keys():
        try:
            idx = int(k)
            dm.encounter_states[idx] = True
        except Exception:
            continue

    # If the profile indicates the path is open, ensure the special encounter appears
    if profile.get_flag('path_open'):
        if not any(enc.get('id') == 'path' for enc in encounter_points):
            encounter_points.append({
                "id": "path",
                "pos": pygame.Vector2(screen.get_width() * 0.85, screen.get_height() * 0.3),
                "type": "dialogue",
                "character": "Gatekeeper"
            })

    running = True
    dt = 0
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu_active = not menu_active
                    menu_selection = 0
                elif menu_active:
                    if event.key == pygame.K_UP:
                        menu_selection = (menu_selection - 1) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        menu_selection = (menu_selection + 1) % len(menu_options)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        if menu_selection == 0:  # Continue
                            menu_active = False
                        elif menu_selection == 1:  # Reset Progress
                            profile.clear()
                            dm.encounter_states = {}
                            menu_active = False
                        elif menu_selection == 2:  # Link Online Account
                            threading.Thread(target=lambda: start_pairing(profile), daemon=True).start()
                            menu_active = False
                        elif menu_selection == 3:  # Back to Main Menu
                            running = False

        # Draw game state
        if bg_image:
            try:
                bg_surf = pygame.transform.smoothscale(bg_image, (screen.get_width(), screen.get_height()))
                screen.blit(bg_surf, (0, 0))
            except Exception:
                screen.blit(bg_image, (0, 0))
        else:
            screen.fill("black")

        # Update and draw player
        keys = pygame.key.get_pressed()
        if not menu_active:
            if keys[pygame.K_w]:
                player_pos.y -= 300 * dt
                current_player_image = player_images.get('w', current_player_image)
            elif keys[pygame.K_s]:
                player_pos.y += 300 * dt
                current_player_image = player_images.get('s', current_player_image)
            elif keys[pygame.K_a]:
                player_pos.x -= 300 * dt
                current_player_image = player_images.get('a', current_player_image)
            elif keys[pygame.K_d]:
                player_pos.x += 300 * dt
                current_player_image = player_images.get('d', current_player_image)

        player_rect = current_player_image.get_rect(center=player_pos)
        screen.blit(current_player_image, player_rect)

        # Draw encounter points and handle interactions
        for idx, enc in enumerate(encounter_points):
            pt = enc["pos"]
            color = (0, 255, 255) if not dm.encounter_states.get(idx, False) else (100, 100, 100)
            pygame.draw.circle(screen, color, (int(pt.x), int(pt.y)), 30)

            # Draw badge for chosen options
            choice = profile.get_choice(idx)
            if choice is not None:
                try:
                    sel = int(choice.get('selected', 0))
                    badge_color = [(200, 120, 120), (120, 200, 120), (120, 160, 240)][sel % 3]
                    badge_pos = (int(pt.x + 28), int(pt.y - 28))
                    pygame.draw.circle(screen, badge_color, badge_pos, 12)
                    font = pygame.font.SysFont(None, 20)
                    txt = font.render(str(sel+1), True, (20, 20, 20))
                    txt_rect = txt.get_rect(center=badge_pos)
                    screen.blit(txt, txt_rect)
                except Exception:
                    pass

            # Check for encounters
            if not menu_active and not dm.encounter_states.get(idx, False):
                if player_pos.distance_to(pt) < 60:
                    handle_encounter(screen, dm, profile, enc, idx)

        # Show intro if needed
        dm.narrate_intro(screen)

        # Draw menu if active
        if menu_active:
            draw_menu(screen, menu_options, menu_selection)

        pygame.display.flip()
        dt = clock.tick(60) / 1000

    pygame.quit()

if __name__ == "__main__":
    main()