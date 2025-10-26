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
        # load background
        self.bg_raw = pygame.image.load(bg_path).convert()

        # store callback for scene changes
        self.game_state_callback = game_state_callback

        # font / UI text
        self.font = pygame.font.Font(None, 32)
        self.text_color = (255, 255, 255)
        self.dialog_text = "Select a planet to get started"

        # clickable 'planets' as circle hitboxes.
        # YOU will tune these numbers to match where the planets are drawn.
        # pos: (x, y), radius: int, id: string
        self.planets = [
            {"pos": (200, 100), "radius": 50, "id": "planet1"},
            {"pos": (500, 360), "radius": 60, "id": "planet2"},
            {"pos": (1150, 370), "radius": 65, "id": "planet3"},
        ]

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
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]

        for planet in self.planets:
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

    def draw(self, screen):
        """
        Full render of this screen.
        Order matters: background -> circles -> textbox
        """
        self._draw_background_scaled(screen)
        self._draw_planet_circles(screen)
        self._draw_textbox(screen)
