import pygame
from mainMenu import MainMenu
from play_screen import PlayScreen


class SpaceCowboyGame:
    def __init__(self, width=1280, height=720, title="Space Cowboy"):
        pygame.init()

        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0

        # --- screen state ---
        self.current_screen = "menu"

        # create play screen now so it's ready
        self.play_screen = PlayScreen(
            bg_path="/Users/nerd/the-wranglers-game/space-cowboys-game/assets/images/Sherriff_station_boss_locked.png"
        )

        # create menu and give it a callback to switch to play
        self.main_menu = MainMenu(on_play=self.go_to_play)

    def go_to_play(self):
        """Called when 'Play' is clicked."""
        self.current_screen = "play"

    def go_to_menu(self):
        """Optional: you can call this later (ESC, etc.)."""
        self.current_screen = "menu"

    def handle_events(self):
        """Handle user and system events."""
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                # Recreate the display surface so new size is honored
                self.screen = pygame.display.set_mode(
                    (event.w, event.h), pygame.RESIZABLE
                )
                # no re-render call here; render() will run anyway this frame

            if event.type == pygame.QUIT:
                self.running = False

            # bonus: allow ESC to go back to menu from play
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.go_to_menu()

    def update(self):
        """Future logic per-screen if you need it."""
        # For now, nothing to update continuously.
        pass

    def render(self):
        """Render the active screen."""
        if self.current_screen == "menu":
            # black background for menu
            self.screen.fill("black")
            self.main_menu.load_main_menu(self.screen)

        elif self.current_screen == "play":
            # draw sheriff station + textbox
            self.play_screen.draw(self.screen)

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
