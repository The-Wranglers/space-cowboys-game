import pygame

class MainMenu:
    def __init__(self):
        pygame.font.init()
        self.font = pygame.font.Font(None, 60)

    def load_main_menu(self, screen):
        text_surface = self.font.render("Main Menu", True, (255, 255, 255))
        play_text = self.font.render("Play", True, (255, 255, 255))
        leadership_text = self.font.render("Leadership Board", True, (255, 255, 255))
        instruction_text = self.font.render("Instructions", True, (255, 255, 255))
        
        # Main Menu Text
        text_rect = text_surface.get_rect(center=(screen.get_width() / 2, 80))
        screen.blit(text_surface, text_rect)
        # Play Text 
        play_rect = play_text.get_rect(center=(screen.get_width() / 2, 120))
        screen.blit(play_text, play_rect)
        # Leadership Board Text
        leadership_rect = leadership_text.get_rect(center=(screen.get_width() / 2, 140))
        screen.blit(leadership_text, text_rect)
        # Instructions 
        instruction_rect = instruction_text.get_rect(center=(screen.get_width() / 2, 180))
        screen.blit(instruction_text, instruction_rect)

    def load_options(self, screen):
        pass
