import pygame


GREEN = (0, 255, 0)
WIDTH, HEIGHT = 20


class Food(pygame.draw.rect):
    def __init__(self, Surface, row, column):
        self.Surface = Surface
        self.color = GREEN
        # Set position in grid
        self.row = row
        self.column = column
        # Calculate and set position on screen
        left = row * WIDTH
        top = column * HEIGHT
        self.Rect = [left, top, WIDTH, HEIGHT]
        # Make solid
        self.width = 0
