import pygame
from mainMenu import MainMenu


class SpaceCowboyGame:
    def __init__(self, width=1280, height=720, title="Space Cowboy"):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        self.player_pos = pygame.Vector2(self.screen.get_width() / 2, self.screen.get_height() / 2)
        self.main_menu = MainMenu()

    def handle_events(self):
        """Handle user and system events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        """Update game logic (e.g., animations, player movement, etc.)."""
        # Placeholder for future game logic
        pass

    def render(self):
        """Render everything to the screen."""
        self.screen.fill("black")
        self.main_menu.load_main_menu(self.screen)
        self.main_menu.load_options(self.screen)
        pygame.display.flip()

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.dt = self.clock.tick(60) / 1000  # delta time in seconds
        pygame.quit()


if __name__ == "__main__":
    game = SpaceCowboyGame()
    game.run()
