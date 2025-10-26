import pygame

class MainMenu:
    def __init__(self, on_play=None):
        pygame.font.init()
        from utils.window_state import WindowState
        self.window_state = WindowState.get_instance()
        
        # Reference dimensions for consistent scaling
        self.REF_WIDTH = 1280
        self.REF_HEIGHT = 720
        
        # base fonts will be created per-screen so they scale with resolution
        self.font = None
        self.hover_font = None

        # load raw background and defer scaling to when we know the screen size
        self._raw_bg = pygame.image.load('./assets/images/Cowboy image.png').convert()
        self._scaled_bg = None
        self._last_screen_size = None

        # callback to tell the game "go to play"
        self.on_play = on_play

        self.options = [
            {"label": "Play", "id": "play"},
            {"label": "Leadership Board", "id": "leaderboard"},
            {"label": "Instructions", "id": "instructions"},
        ]

    def load_main_menu(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]

        sw = screen.get_width()
        sh = screen.get_height()

        # Recompute scaled resources & fonts if resolution changed
        if self._last_screen_size != (sw, sh):
            # scale background relative to reference size
            raw_w, raw_h = self._raw_bg.get_size()
            ref_scale = min(sw / self.REF_WIDTH, sh / self.REF_HEIGHT)
            target_bg_w = max(120, int(raw_w * ref_scale * 0.25))
            target_bg_h = max(120, int(raw_h * ref_scale * 0.25))
            self._scaled_bg = pygame.transform.smoothscale(self._raw_bg, (target_bg_w, target_bg_h))

            # compute font sizes relative to screen height
            title_size = max(20, int(sh * 0.08))
            option_size = max(14, int(sh * 0.05))
            hover_size = max(option_size + 6, int(sh * 0.06))

            self.font = pygame.font.Font(None, option_size)
            self.hover_font = pygame.font.Font(None, hover_size)
            self._title_font = pygame.font.Font(None, title_size)

            self._last_screen_size = (sw, sh)

        # Title text
        title_surface = self._title_font.render("Main Menu", True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(sw // 2, int(sh * 0.12)))

        # Draw background art and title (centered under title)
        bg_x = sw // 2 - (self._scaled_bg.get_width() // 2)
        bg_y = int(sh * 0.18)
        screen.blit(self._scaled_bg, (bg_x, bg_y))
        screen.blit(title_surface, title_rect)

        # Menu options list (start below bg image)
        start_y = bg_y + self._scaled_bg.get_height() + int(sh * 0.05)
        spacing = max(24, int(sh * 0.07))
        clicked_id = None

        for option in self.options:
            label = option["label"]

            # default text style
            text_surface = self.font.render(label, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(sw // 2, start_y))

            # hover style (larger font)
            if text_rect.collidepoint(mouse_pos):
                text_surface = self.hover_font.render(label, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(sw // 2, start_y))
                screen.blit(text_surface, text_rect)

                if mouse_click:
                    clicked_id = option["id"]
            else:
                screen.blit(text_surface, text_rect)

            start_y += spacing

        # Handle click result after loop so one click doesn't trigger multiple
        if clicked_id == "play":
            if self.on_play:
                self.on_play()  # tell game to switch screens

        elif clicked_id == "leaderboard":
            print("Leadership clicked (future: go to leaderboard)")

        elif clicked_id == "instructions":
            print("Instructions clicked (future: go to instructions)")
