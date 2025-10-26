import pygame

class MainMenu:
    def __init__(self):
        self.WHITE = (255, 255, 255)
        self.BLUE = (0, 128, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 200, 0)
        pygame.font.init()
        self.MENUPATH = pygame.image.load('./assets/images/main-menu-screen.png')
    def load_main_menu(self,screen):
        screen.blit(self.MENUPATH, (0,0))

    def load_options(self, screen):
        menu_options = {
            'play': pygame.Rect(100, 100, 200, 80),
            'leadership': pygame.Rect(100, 100, 200, 80),
            'instructions': pygame.Rect(100, 100, 200, 80),
        }
        pygame.draw.rect(screen, self.BLUE, menu_options["play"])
        pygame.draw.rect(screen, self.BLUE, menu_options["leadership"])
        pygame.draw.rect(screen, self.BLUE, menu_options["instructions"])
