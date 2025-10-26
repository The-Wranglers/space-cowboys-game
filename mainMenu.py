import pygame

class MainMenu:
    def __init__(self, on_play=None):
        pygame.font.init()
        self.font = pygame.font.Font(None, 60)
        self.hover_font = pygame.font.Font(None, 70)  # bigger on hover

        # load once
        raw_bg = pygame.image.load('./assets/images/Cowboy image.png').convert()
        # scale once instead of every frame
        self.scaled_bg = pygame.transform.scale(raw_bg, (300, 400))

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

        # Title text
        title_surface = self.font.render("Main Menu", True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(screen.get_width() / 2, 80))

        # Draw background art and title
        screen.blit(self.scaled_bg, (screen.get_width() / 2 - 157, 80))
        screen.blit(title_surface, title_rect)

        # Menu options list
        start_y = 500
        clicked_id = None

        for option in self.options:
            label = option["label"]

            # default text style
            text_surface = self.font.render(label, True, (255, 255, 255))
            text_rect = text_surface.get_rect(
                center=(screen.get_width() / 2, start_y)
            )

            # hover style (larger font)
            if text_rect.collidepoint(mouse_pos):
                text_surface = self.hover_font.render(
                    label, True, (255, 255, 255)
                )
                text_rect = text_surface.get_rect(
                    center=(screen.get_width() / 2, start_y)
                )
                screen.blit(text_surface, text_rect)

                if mouse_click:
                    clicked_id = option["id"]
            else:
                screen.blit(text_surface, text_rect)

            start_y += 80  # vertical spacing

        # Handle click result after loop so one click doesn't trigger multiple
        if clicked_id == "play":
            if self.on_play:
                self.on_play()  # tell game to switch screens

        elif clicked_id == "leaderboard":
            print("Leadership clicked (future: go to leaderboard)")

        elif clicked_id == "instructions":
            print("Instructions clicked (future: go to instructions)")
