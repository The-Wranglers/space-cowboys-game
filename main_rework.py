import pygame
from mainMenu import MainMenu
from play_screen import PlayScreen


class SpaceCowboyGame:
    """
    Game root. Handles window, loop, and which screen is active.
    """

    def __init__(self, width=1280, height=720, title="Space Cowboy"):
        pygame.init()

        # Initialize window state singleton
        from utils.window_state import WindowState
        self.window_state = WindowState.get_instance()
        self.window_state.update_size(width, height)
        
        # Create screen using window state
        self.screen = self.window_state.create_screen()
        pygame.display.set_caption(title)

        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0.0  # delta time per frame in seconds

        # which screen are we currently showing
        # valid states: "menu", "play", "sheriff_level"
        self.current_screen = "menu"

        # create play/planet-select screen
        self.play_screen = PlayScreen(
            bg_path="./assets/images/Sherriff_station_boss_locked.png",
            game_state_callback=self.change_screen  # <-- this is now valid
        )

        # create main menu and inject callback to start playing
        self.main_menu = MainMenu(on_play=self.go_to_play)

    # ---- state change helpers ----
    def change_screen(self, new_state):
        """
        This lets other screens (like PlayScreen) tell the game
        to switch to something else, e.g. 'sheriff_level'.
        """
        self.current_screen = new_state

    def go_to_play(self):
        """Called when 'Play' is clicked in MainMenu."""
        self.current_screen = "play"

    def go_to_menu(self):
        """Return to main menu."""
        self.current_screen = "menu"

    # ---- event loop ----
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.VIDEORESIZE:
                # Update window state and recreate screen
                self.window_state.update_size(event.w, event.h)
                self.screen = self.window_state.create_screen()

            elif event.type == pygame.KEYDOWN:
                # ESC -> back to menu for now no matter what
                if event.key == pygame.K_ESCAPE:
                    self.go_to_menu()

    def update(self):
        # nothing animated yet; placeholder for future logic
        pass

    def render(self):
        # draw based on current_screen value
        if self.current_screen == "menu":
            self.screen.fill("black")
            self.main_menu.load_main_menu(self.screen)

        elif self.current_screen == "play":
            self.play_screen.draw(self.screen)

        elif self.current_screen == "sheriff_level":
            # temporary placeholder until you build that screen
            self.screen.fill((20, 0, 0))
            debug_font = pygame.font.Font(None, 50)
            debug_text = debug_font.render(
                "Sheriff Level Loaded",
                True,
                (255, 255, 255)
            )
            rect = debug_text.get_rect(
                center=(
                    self.screen.get_width() / 2,
                    self.screen.get_height() / 2
                )
            )
            self.screen.blit(debug_text, rect)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()

            # lock frame rate ~60 FPS, capture delta time
            self.dt = self.clock.tick(60) / 1000.0

        pygame.quit()


if __name__ == "__main__":
    game = SpaceCowboyGame()
    game.run()
