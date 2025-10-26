import pygame
from DanielsWorld.adventure_map import AdventureMap
from DanielsWorld.maps import DungeonMaster, ai_generate_dialogue, run_sebs_minigame, run_presleyworld_minigame
import os


# Path to World1Map.png (adjust if needed)
WORLD1_MAP_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'images', 'World1Map.png')


class PlayScreen:
    def __init__(self, bg_path, game_state_callback=None):
        """
        bg_path: background image for this screen
        game_state_callback: a function we can call to tell the game
                             to change screens (ex: 'sheriff_level')
        """
        from utils.window_state import WindowState
        self.window_state = WindowState.get_instance()
        
        # load background
        self.bg_raw = pygame.image.load(bg_path).convert()

        # store callback for scene changes
        self.game_state_callback = game_state_callback

        # font / UI text
        base_font_size = int(32 * (self.window_state.height / 720))  # Scale font relative to reference height
        self.font = pygame.font.Font(None, base_font_size)
        self.text_color = (255, 255, 255)
        self.dialog_text = "Select a planet to get started"

        # clickable 'planets' as circle hitboxes.
        # YOU will tune these numbers to match where the planets are drawn.
        # pos: (x, y), radius: int, id: string
        # The values below are treated as positions/radii in the background image's pixel space
        # and will be converted to relative ratios so resizing preserves layout.
        self.planets = [
            {"pos": (92, 75), "radius": 60, "id": "planet1"},
            {"pos": (475, 330), "radius": 55, "id": "planet2"},
            {"pos": (865, 160), "radius": 45, "id": "planet3"},
            {"pos": (1145, 355), "radius": 85, "id": "planet4"},
        ]

        # store normalized ratios based on the background image size so we can
        # recompute absolute positions when the window resizes
        self._bg_size = self.bg_raw.get_size()  # (width, height)
        self._compute_normalized_planets()

        # cached absolute planet positions for current window size
        self._last_screen_size = None
        self._planets_abs = None

    def _wrap_text(self, text, max_width):
        """Wrap dialog_text into multiple lines so it fits in the box."""
        words = text.split(" ")
        lines = []
        cur_line = ""

        for w in words:
            test_line = (cur_line + " " + w).strip()
            surf = self.font.render(test_line, True, self.text_color)
            if surf.get_width() <= max_width:
                cur_line = test_line
            else:
                lines.append(cur_line)
                cur_line = w

        if cur_line:
            lines.append(cur_line)

        return lines

    def _draw_background_scaled(self, screen):
        """Scale background to window size and draw it."""
        sw = screen.get_width()
        sh = screen.get_height()
        bg_scaled = pygame.transform.scale(self.bg_raw, (sw, sh))
        screen.blit(bg_scaled, (0, 0))

    def _draw_textbox(self, screen):
        """Bottom dialog/instruction box."""
        sw = screen.get_width()
        sh = screen.get_height()

        box_h = int(sh * 0.22)
        box_rect = pygame.Rect(0, sh - box_h, sw, box_h)

        # black box
        pygame.draw.rect(screen, (0, 0, 0), box_rect)
        # light border
        pygame.draw.rect(screen, (200, 200, 200), box_rect, 2)

        # wrap text
        padding_x = 20
        padding_y = 20
        usable_width = sw - (padding_x * 2)
        lines = self._wrap_text(self.dialog_text, usable_width)

        # draw lines
        y = box_rect.top + padding_y
        for line in lines:
            surf = self.font.render(line, True, self.text_color)
            screen.blit(surf, (box_rect.left + padding_x, y))
            y += surf.get_height() + 8

    def _draw_planet_circles(self, screen):
        """
        Draws hoverable/clickable outlines for each planet.
        - Default: dim white ring
        - Hover: brighter/yellowish, thicker
        - Click: triggers action (right now print + optional scene switch)
        """
        # ensure absolute positions are up-to-date for current screen size
        if self._last_screen_size != (screen.get_width(), screen.get_height()):
            self._recalc_planets_for_screen(screen)

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]

        for planet in self._planets_abs:
            x, y = planet["pos"]
            r = planet["radius"]

            # distance from mouse to circle center
            dx = mouse_pos[0] - x
            dy = mouse_pos[1] - y
            dist = (dx * dx + dy * dy) ** 0.5
            hovered = dist <= r

            if hovered:
                color = (255, 255, 100)  # brighter when hovered
                width = 4
            else:
                color = (255, 255, 255)
                width = 2

            # draw circle outline
            pygame.draw.circle(screen, color, (x, y), r, width)

            # click behavior
            if hovered and mouse_click:
                planet_id = planet["id"]
                print(f"{planet_id} clicked")
                if planet_id == "planet1":
                    # Launch AdventureMap for planet1 with World1Map.png
                    adventure = AdventureMap(WORLD1_MAP_PATH)
                    adventure.run(DungeonMaster, ai_generate_dialogue, run_sebs_minigame, run_presleyworld_minigame)
                elif planet_id == "planet2" and self.game_state_callback:
                    self.game_state_callback("sheriff_level")

    def _compute_normalized_planets(self):
        """Compute normalized ratios (x_ratio, y_ratio, radius_ratio) from image-space planets."""
        bw, bh = self._bg_size
        self._planets_norm = []
        # radius normalized relative to shorter side so it scales well
        base_dim = min(bw, bh) if min(bw, bh) > 0 else max(bw, bh)
        for p in self.planets:
            x, y = p["pos"]
            r = p["radius"]
            x_ratio = x / bw if bw else 0.5
            y_ratio = y / bh if bh else 0.5
            r_ratio = r / base_dim if base_dim else 0.05
            self._planets_norm.append({
                "id": p.get("id"),
                "x_ratio": x_ratio,
                "y_ratio": y_ratio,
                "r_ratio": r_ratio,
            })

    def _recalc_planets_for_screen(self, screen):
        """Recalculate absolute planet positions from normalized ratios for current screen size."""
        sw, sh = screen.get_width(), screen.get_height()
        base_dim = min(sw, sh) if min(sw, sh) > 0 else max(sw, sh)
        abs_list = []
        for p in self._planets_norm:
            x = int(p["x_ratio"] * sw)
            y = int(p["y_ratio"] * sh)
            r = max(4, int(p["r_ratio"] * base_dim))
            abs_list.append({"id": p["id"], "pos": (x, y), "radius": r})
        self._planets_abs = abs_list
        self._last_screen_size = (sw, sh)

    def draw(self, screen):
        """
        Full render of this screen.
        Order matters: background -> circles -> textbox
        """
        self._draw_background_scaled(screen)
        self._draw_planet_circles(screen)
        self._draw_textbox(screen)
