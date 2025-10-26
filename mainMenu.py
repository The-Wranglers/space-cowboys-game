import pygame

class MainMenu:
    def __init__(self, on_play=None):
        pygame.font.init()
        self.font = pygame.font.Font(None, 60)
        self.hover_font = pygame.font.Font(None, 70)  # slightly larger for hover

        # load once
        self.background_image = pygame.image.load('./assets/images/Cowboy image.png').convert()

        # store a function the game passes us so we can tell it "switch to play"
        self.on_play = on_play

        self.options = [
            {"label": "Play", "id": "play"},
            {"label": "Leadership Board", "id": "leaderboard"},
            {"label": "Instructions", "id": "instructions"},
        ]

    def load_main_menu(self, screen):
        # scale cowboy art every frame to keep aspect predictable
        # NOTE: if you don't want this done every frame, pre-scale in __init__
        scaled_bg = pygame.transform.scale(self.background_image, (300, 400))

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]

        # Title text
        title_surface = self.font.render("Main Menu", True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(screen.get_width() / 2, 80))

        # Draw background art and title
        screen.blit(scaled_bg, (screen.get_width() / 2 - 157, 80))
        screen.blit(title_surface, title_rect)

        # Start drawing menu items under the image
        start_y = 500
        clicked_id = None

        for option in self.options:
            label = option["label"]

            # Normal style
            text_surface = self.font.render(label, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(screen.get_width() / 2, start_y))

            # Hover style (larger font)
            if text_rect.collidepoint(mouse_pos):
                text_surface = self.hover_font.render(label, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(screen.get_width() / 2, start_y))
                screen.blit(text_surface, text_rect)

                if mouse_click:
                    clicked_id = option["id"]
            else:
                screen.blit(text_surface, text_rect)

            start_y += 80  # spacing between menu items

        # Handle click result after loop so one click doesn't trigger multiple items
        if clicked_id == "play":
            if self.on_play:
                self.on_play()  # tell game to switch screens

        elif clicked_id == "leaderboard":
            print("Leadership clicked (future: go to leaderboard)")
        elif clicked_id == "instructions":
            print("Instructions clicked (future: go to instructions)")
