import pygame

class MainMenu:
    def __init__(self):
        pygame.font.init()
        self.font = pygame.font.Font(None, 60)
        self.hover_font = pygame.font.Font(None, 70)  # slightly larger for hover
        self.options = [
            {"label": "Play", "action": self.play_action},
            {"label": "Leadership Board", "action": self.leadership_action},
            {"label": "Instructions", "action": self.instructions_action},
        ]

    def play_action(self):
        print("Play clicked (future: go to game screen)")

    def leadership_action(self):
        print("Leadership clicked (future: go to leaderboard)")

    def instructions_action(self):
        print("Instructions clicked (future: go to instructions)")

    def load_main_menu(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        title_surface = self.font.render("Main Menu", True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(screen.get_width() / 2, 80))
        screen.blit(title_surface, title_rect)

        start_y = 160
        for option in self.options:
            font = self.font
            text_color = (255, 255, 255)
            label = option["label"]

            # Create text surface and rect
            text_surface = font.render(label, True, text_color)
            text_rect = text_surface.get_rect(center=(screen.get_width() / 2, start_y))

            # Detect hover
            if text_rect.collidepoint(mouse_pos):
                text_surface = self.hover_font.render(label, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(screen.get_width() / 2, start_y))

                # Simple scale-up animation on hover
                screen.blit(text_surface, text_rect)

                # Handle click
                if mouse_click:
                    option["action"]()
            else:
                screen.blit(text_surface, text_rect)

            start_y += 80  # spacing between menu items
