"""
Maintains window state (size, scale) across different scenes.
"""
import pygame

class WindowState:
    _instance = None
    
    def __init__(self):
        if WindowState._instance is not None:
            raise Exception("WindowState is a singleton!")
        self.width = 1280  # Default width
        self.height = 720  # Default height
        self.scale = 1.0   # Current scale factor
        WindowState._instance = self
    
    @staticmethod
    def get_instance():
        if WindowState._instance is None:
            WindowState()
        return WindowState._instance
    
    def update_size(self, width, height):
        """Update window size and adjust scale"""
        self.width = width
        self.height = height
    
    def get_size(self):
        """Get current window size"""
        return (self.width, self.height)
    
    def create_screen(self):
        """Create a pygame screen with current dimensions"""
        return pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)