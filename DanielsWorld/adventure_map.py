import pygame
import sys
import os
from pathlib import Path
import random
from player_profile import PlayerProfile
import importlib
import logging

# logger to report which encounter generator was used and the final placements
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# Ensure project root is importable so DanielsWorld.encounters_config can be imported
project_root = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(project_root))

class AdventureMap:
    def __init__(self, map_image_path, window_size=(1280, 720), window_title="Adventure Map",
                 encounter_generator=None, obstacle_generator=None):
        pygame.init()
        self.screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)
        pygame.display.set_caption(window_title)
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        self.project_root = Path(__file__).resolve().parents[1]
        self.bg_image = None
        self.map_image_path = map_image_path
        self.load_background()
        self.player_images = self.load_player_images()
        self.current_player_image = self.player_images.get('a')
        self.player_pos = pygame.Vector2(self.screen.get_width() / 2, self.screen.get_height() / 2)
        self.player_rect = self.current_player_image.get_rect(center=self.player_pos)
        self.profile = PlayerProfile()
        # If an encounter_generator was explicitly provided, use it. Otherwise try to
        # import `DanielsWorld.encounters_config.generate_encounters(screen)` and use that.
        if encounter_generator:
            self.encounter_points = encounter_generator(self.screen)
            self._encounter_source = 'custom_generator'
        else:
            try:
                enc_mod = importlib.import_module('DanielsWorld.encounters_config')
                if hasattr(enc_mod, 'generate_encounters'):
                    self.encounter_points = enc_mod.generate_encounters(self.screen)
                    self._encounter_source = 'DanielsWorld.encounters_config:generate_encounters'
                elif hasattr(enc_mod, 'encounter_generator'):
                    # support alternate name
                    self.encounter_points = enc_mod.encounter_generator(self.screen)
                    self._encounter_source = 'DanielsWorld.encounters_config:encounter_generator'
                else:
                    self.encounter_points = self.default_encounters()
                    self._encounter_source = 'default_encounters'
            except Exception:
                # fallback to built-in defaults
                self.encounter_points = self.default_encounters()
                self._encounter_source = 'default_encounters'

        # Normalize encounter positions to a reference size (bg image if available, else current screen)
        try:
            from utils.ui_scaling import get_ref_size, set_encounters_normalized, recalc_encounter_positions
            ref_size = get_ref_size(self.bg_image, self.screen)
            set_encounters_normalized(self.encounter_points, ref_size)
            # ensure absolute positions are set for current screen
            recalc_encounter_positions(self.encounter_points, self.screen, ref_size)
            self._encounter_ref_size = ref_size
        except Exception:
            # fallback — leave encounters as-is
            self._encounter_ref_size = (self.screen.get_width(), self.screen.get_height())

        # Log which source produced the encounter points and enumerate them for debugging
        try:
            logger.info("Encounter generator source: %s", getattr(self, '_encounter_source', 'unknown'))
            for i, enc in enumerate(self.encounter_points):
                pos = enc.get('pos')
                # pos may be a pygame.Vector2; present as tuple
                if hasattr(pos, 'x') and hasattr(pos, 'y'):
                    pos_repr = f"({int(pos.x)},{int(pos.y)})"
                else:
                    pos_repr = str(pos)
                logger.info("Encounter %d: id=%s type=%s pos=%s", i, enc.get('id'), enc.get('type'), pos_repr)
        except Exception:
            # Logging should never crash initialization
            pass
        self.obstacles = obstacle_generator(self.screen) if obstacle_generator else []
        self.dm = None  # DungeonMaster instance, set in run()

    def load_background(self):
        try:
            if self.map_image_path and Path(self.map_image_path).exists():
                self.bg_image = pygame.image.load(str(self.map_image_path)).convert()
            else:
                print(f"Background image not found at {self.map_image_path}", file=sys.stderr)
        except Exception as e:
            print(f"Failed to load background image: {e}", file=sys.stderr)
            self.bg_image = None

    def load_player_images(self):
        player_images = {}
        for direction in ['w', 'a', 's', 'd']:
            try:
                img_path = self.project_root / "assets" / "images" / f"{direction}Capy.png"
                player_images[direction] = pygame.image.load(str(img_path))
            except Exception as e:
                print(f"Failed to load player image {direction}Capy.png: {e}", file=sys.stderr)
        if not player_images.get('a'):
            surf = pygame.Surface((80, 80))
            surf.fill("red")
            player_images['a'] = surf
        return player_images

    def default_encounters(self):
        w, h = self.screen.get_width(), self.screen.get_height()
        return [
            {"id": "enc0", "pos": pygame.Vector2(w * 0.3, h * 0.4), "type": "dialogue", "character": "Mysterious Stranger"},
            {"id": "enc1", "pos": pygame.Vector2(w * 0.7, h * 0.6), "type": "minigame"},
            {"id": "enc2", "pos": pygame.Vector2(w * 0.5, h * 0.8), "type": "dialogue", "character": "Lost Robot"},
        ]

    def run(self, DungeonMasterClass, ai_generate_dialogue, run_sebs_minigame, run_presleyworld_minigame):
        self.dm = DungeonMasterClass()
        # Load profile choices and mark encounters done if present
        for k in self.profile.choices().keys():
            try:
                idx = int(k)
                self.dm.encounter_states[idx] = True
            except Exception:
                continue

        running = True
        dt = 0
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    # Recalculate encounter positions for new window size
                    try:
                        from utils.ui_scaling import recalc_encounter_positions
                        recalc_encounter_positions(self.encounter_points, self.screen, getattr(self, '_encounter_ref_size', (self.screen.get_width(), self.screen.get_height())))
                    except Exception:
                        pass
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        menu_active = True
                        menu_selection = 0
                        menu_options = ["Continue", "Reset Progress", "Link Online Account", "Back to Main Menu"]
                        menu_result = None
                        while menu_active and running:
                            for menu_event in pygame.event.get():
                                if menu_event.type == pygame.QUIT:
                                    menu_active = False
                                    running = False
                                elif menu_event.type == pygame.KEYDOWN:
                                    if menu_event.key == pygame.K_ESCAPE:
                                        menu_active = False
                                    elif menu_event.key == pygame.K_UP:
                                        menu_selection = (menu_selection - 1) % len(menu_options)
                                    elif menu_event.key == pygame.K_DOWN:
                                        menu_selection = (menu_selection + 1) % len(menu_options)
                                    elif menu_event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                                        if menu_selection == 0:
                                            menu_active = False
                                        elif menu_selection == 1:
                                            self.profile.clear()
                                            self.dm.encounter_states = {}
                                            menu_active = False
                                        elif menu_selection == 2:
                                            # Not implemented: link online account
                                            menu_active = False
                                        elif menu_selection == 3:
                                            # Back to Main Menu
                                            menu_active = False
                                            running = False
                                            menu_result = "main_menu"
                            # Draw darkened background
                            dark_overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
                            dark_overlay.fill((0, 0, 0))
                            dark_overlay.set_alpha(128)
                            self.screen.blit(dark_overlay, (0, 0))
                            menu_font = pygame.font.SysFont(None, 36)
                            menu_title = menu_font.render("Menu", True, (255, 255, 0))
                            title_rect = menu_title.get_rect(centerx=self.screen.get_width() // 2, top=self.screen.get_height() // 3)
                            self.screen.blit(menu_title, title_rect)
                            for i, option in enumerate(menu_options):
                                color = (255, 255, 0) if i == menu_selection else (200, 200, 200)
                                text = menu_font.render(option, True, color)
                                text_rect = text.get_rect(centerx=self.screen.get_width() // 2, top=title_rect.bottom + 40 + i * 40)
                                if i == menu_selection:
                                    pygame.draw.rect(self.screen, color, text_rect.inflate(20, 5), 1)
                                self.screen.blit(text, text_rect)
                            pygame.display.flip()
                        if menu_result == "main_menu":
                            return "main_menu"

            # draw background
            if self.bg_image:
                try:
                    bg_surf = pygame.transform.smoothscale(self.bg_image, (self.screen.get_width(), self.screen.get_height()))
                    self.screen.blit(bg_surf, (0, 0))
                except Exception:
                    self.screen.blit(self.bg_image, (0, 0))
            else:
                self.screen.fill("black")

            # Update player image based on movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                self.current_player_image = self.player_images.get('w', self.current_player_image)
            elif keys[pygame.K_s]:
                self.current_player_image = self.player_images.get('s', self.current_player_image)
            elif keys[pygame.K_a]:
                self.current_player_image = self.player_images.get('a', self.current_player_image)
            elif keys[pygame.K_d]:
                self.current_player_image = self.player_images.get('d', self.current_player_image)

            # Draw player
            self.player_rect = self.current_player_image.get_rect(center=self.player_pos)
            self.screen.blit(self.current_player_image, self.player_rect)

            # Draw encounter points
            for idx, enc in enumerate(self.encounter_points):
                pt = enc["pos"]
                color = (0, 255, 255) if not self.dm.encounter_states.get(idx, False) else (100, 100, 100)
                pygame.draw.circle(self.screen, color, (int(pt.x), int(pt.y)), 30)
                # draw a small badge/icon if player has chosen an option for this encounter
                choice = self.profile.get_choice(idx)
                if choice is not None:
                    try:
                        sel = int(choice.get('selected', 0))
                    except Exception:
                        sel = 0
                    badge_color = [(200, 120, 120), (120, 200, 120), (120, 160, 240)][sel % 3]
                    badge_pos = (int(pt.x + 28), int(pt.y - 28))
                    pygame.draw.circle(self.screen, badge_color, badge_pos, 12)
                    try:
                        font = pygame.font.SysFont(None, 20)
                        txt = font.render(str(sel+1), True, (20, 20, 20))
                        txt_rect = txt.get_rect(center=badge_pos)
                        self.screen.blit(txt, txt_rect)
                    except Exception:
                        pass

            # AI DM intro
            self.dm.narrate_intro(self.screen)

            # Check for encounter proximity
            for idx, enc in enumerate(self.encounter_points):
                pt = enc["pos"]
                if not self.dm.encounter_states.get(idx, False):
                    if self.player_pos.distance_to(pt) < 60:
                        if enc.get("type") == "dialogue":
                            character = enc.get("character", "Stranger")
                            dialogue = ai_generate_dialogue(character)
                            prompt = dialogue["prompt"]
                            options = dialogue["options"]
                            loop_count = 0
                            max_loops = 3
                            keep_looping = True
                            while keep_looping and loop_count < max_loops:
                                self.dm.show_message(self.screen, f"{character}: {prompt}", duration=1.0)
                                font = pygame.font.SysFont(None, 28)
                                box_width = int(self.screen.get_width() * 0.8)
                                box_x = (self.screen.get_width() - box_width) // 2
                                box_y = 130
                                box_height = 48 * len(options) + 20
                                box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
                                s = pygame.Surface((box_rect.w, box_rect.h), pygame.SRCALPHA)
                                s.fill((40, 40, 40, 220))
                                self.screen.blit(s, (box_rect.x, box_rect.y))
                                pygame.draw.rect(self.screen, (255, 255, 0), box_rect, width=2, border_radius=12)
                                current_sel = 0
                                persisted = self.profile.get_choice(idx)
                                if persisted is not None:
                                    try:
                                        current_sel = int(persisted.get('selected', 0))
                                    except Exception:
                                        current_sel = 0
                                def render_options(highlight):
                                    for i, opt in enumerate(options):
                                        y = box_y + 16 + i*48
                                        opt_rect = pygame.Rect(box_x + 12, y, box_width - 24, 40)
                                        if i == highlight:
                                            pygame.draw.rect(self.screen, (60, 90, 60, 180), opt_rect, border_radius=8)
                                        msg = font.render(f"{i+1}. {opt['text']}", True, (220, 255, 220) if i == highlight else (180, 220, 180))
                                        self.screen.blit(msg, (box_x + 28, y + 8))
                                    instr = font.render("Use ↑/↓ to move, Enter to choose, or press number key", True, (200,200,200))
                                    self.screen.blit(instr, (box_x + 20, box_y + box_rect.h - 28))
                                    pygame.display.flip()
                                render_options(current_sel)
                                selected = None
                                while selected is None:
                                    for event in pygame.event.get():
                                        if event.type == pygame.QUIT:
                                            pygame.quit()
                                            sys.exit()
                                        elif event.type == pygame.KEYDOWN:
                                            if event.key == pygame.K_UP:
                                                current_sel = (current_sel - 1) % len(options)
                                                if self.bg_image:
                                                    bg_surf = pygame.transform.smoothscale(self.bg_image, (self.screen.get_width(), self.screen.get_height()))
                                                    self.screen.blit(bg_surf, box_rect, box_rect)
                                                else:
                                                    pygame.draw.rect(self.screen, (0,0,0), box_rect)
                                                pygame.draw.rect(self.screen, (255,255,0), box_rect, width=2, border_radius=12)
                                                render_options(current_sel)
                                            elif event.key == pygame.K_DOWN:
                                                current_sel = (current_sel + 1) % len(options)
                                                if self.bg_image:
                                                    bg_surf = pygame.transform.smoothscale(self.bg_image, (self.screen.get_width(), self.screen.get_height()))
                                                    self.screen.blit(bg_surf, box_rect, box_rect)
                                                else:
                                                    pygame.draw.rect(self.screen, (0,0,0), box_rect)
                                                pygame.draw.rect(self.screen, (255,255,0), box_rect, width=2, border_radius=12)
                                                render_options(current_sel)
                                            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                                                selected = current_sel
                                                break
                                            elif pygame.K_1 <= event.key <= pygame.K_9:
                                                num = event.key - pygame.K_1
                                                if 0 <= num < len(options):
                                                    selected = num
                                                    break
                                followup = options[selected].get('followup', '')
                                option_text = options[selected].get('text', '').lower()
                                followup_text = followup.lower()
                                if ("riddle" in option_text or "puzzle" in option_text or "riddle" in followup_text or "puzzle" in followup_text):
                                    self.dm.show_message(self.screen, "A mysterious puzzle awaits you...", duration=1.4)
                                    run_presleyworld_minigame()
                                else:
                                    self.dm.show_message(self.screen, followup, duration=1.4)
                                try:
                                    self.profile.set_choice(idx, selected, options[selected].get('text', ''))
                                    eff = options[selected].get('effect')
                                    if isinstance(eff, dict):
                                        for kf, vf in eff.items():
                                            self.profile.set_flag(kf, vf)
                                except Exception:
                                    pass
                                if options[selected].get('loop', False):
                                    prompt = followup
                                    loop_count += 1
                                    keep_looping = True
                                else:
                                    keep_looping = False
                            self.dm.encounter_states[idx] = True
                        else:
                            self.dm.encounter(self.screen, idx)

            # Player movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                self.player_pos.y -= 300 * dt
            if keys[pygame.K_s]:
                self.player_pos.y += 300 * dt
            if keys[pygame.K_a]:
                self.player_pos.x -= 300 * dt
            if keys[pygame.K_d]:
                self.player_pos.x += 300 * dt

            pygame.display.flip()
            dt = self.clock.tick(60) / 1000

        pygame.quit()

# Example usage (for planet.py):
# from DanielsWorld.adventure_map import AdventureMap
# my_map = AdventureMap("/path/to/map.png")
# my_map.run(DungeonMaster, ai_generate_dialogue, run_sebs_minigame, run_presleyworld_minigame)
