import pygame

class PlayScreen:
    def __init__(self, bg_path):
        # Load once
        self.bg_raw = pygame.image.load(bg_path).convert()
        self.font = pygame.font.Font(None, 32)
        self.text_color = (255, 255, 255)

        # You can change this line to whatever the sheriff should say
        self.dialog_text = "Select a planet to get started"

    def _wrap_text(self, text, max_width):
        """Very simple word-wrapper to keep text inside the box."""
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

    def draw(self, screen):
        # Stretch background to current window size
        sw = screen.get_width()
        sh = screen.get_height()
        bg_scaled = pygame.transform.scale(self.bg_raw, (sw, sh))
        screen.blit(bg_scaled, (0, 0))

        # Draw textbox at bottom
        box_h = int(sh * 0.22)
        box_rect = pygame.Rect(0, sh - box_h, sw, box_h)

        # Solid black box and light border
        pygame.draw.rect(screen, (0, 0, 0), box_rect)
        pygame.draw.rect(screen, (200, 200, 200), box_rect, 2)

        # Wrap and render dialog text with padding
        padding_x = 20
        padding_y = 20
        usable_width = sw - (padding_x * 2)

        lines = self._wrap_text(self.dialog_text, usable_width)

        y = box_rect.top + padding_y
        for line in lines:
            surf = self.font.render(line, True, self.text_color)
            screen.blit(surf, (box_rect.left + padding_x, y))
            y += surf.get_height() + 8
