import pygame

class MainMenu:
    def __init__(self):
        # self.WHITE = (255, 255, 255)
        # self.BLUE = (0, 128, 255)
        # self.RED = (255, 0, 0)
        # self.GREEN = (0, 200, 0)
        pygame.font.init()
        self.MENUPATH = pygame.image.load('./assets/images/main-menu-screen-1.png')
    def load_main_menu(self,screen):
        screen.blit(self.MENUPATH, (0,0))

    def load_options(self, screen):
        pass 