import pygame


class Planet:
    """
    Clickable / hoverable planet icon.

    - Scales up on hover
    - Calls on_click when clicked
    - Tracks its own rect
    """

    def __init__(self, image_path: str, pos_center: tuple[int, int],
                 scale: float = 1.0, on_click=None):
        """
        image_path:  path to the planet PNG (should have alpha)
        pos_center:  (x, y) center position on screen
        scale:       base size multiplier
        on_click:    callback function when clicked
        """

        # Load image with alpha. Fail loudly if not found.
        raw_img = pygame.image.load(image_path).convert_alpha()

        # Base scaled size
        w, h = raw_img.get_width(), raw_img.get_height()
        self.base_image = pygame.transform.smoothscale(
            raw_img,
            (int(w * scale), int(h * scale))
        )

        # current_image will swap between base and hover version
        self.current_image = self.base_image
        self.rect = self.current_image.get_rect(center=pos_center)

        self.on_click = on_click

    def update(self, mouse_pos: tuple[int, int], mouse_down: bool) -> None:
        """
        Handles:
        - Hover grow (~10%)
        - Click trigger
        """
        hovered = self.rect.collidepoint(mouse_pos)

        if hovered:
            bw = self.base_image.get_width()
            bh = self.base_image.get_height()

            # hover scale
            enlarged = pygame.transform.smoothscale(
                self.base_image,
                (int(bw * 1.1), int(bh * 1.1))
            )

            # preserve center so it doesn't "jump"
            center_before = self.rect.center
            self.current_image = enlarged
            self.rect = self.current_image.get_rect(center=center_before)

            # Click fired this frame
            if mouse_down and self.on_click:
                self.on_click()

        else:
            # reset to base image
            center_before = self.rect.center
            self.current_image = self.base_image
            self.rect = self.current_image.get_rect(center=center_before)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.current_image, self.rect)


# Example usage for launching a map from a planet:
# from DanielsWorld.adventure_map import AdventureMap
# from DanielsWorld.maps import DungeonMaster, ai_generate_dialogue, run_sebs_minigame, run_presleyworld_minigame
# my_map = AdventureMap("/path/to/your_map_image.png")
# my_map.run(DungeonMaster, ai_generate_dialogue, run_sebs_minigame, run_presleyworld_minigame)
# You can pass custom encounter/obstacle generators to AdventureMap if desired.
