import pygame


BLUE = (0, 0, 255)
WIDTH, HEIGHT = 20


class Organism(pygame.draw.rect):
    def __init__(self, Surface, row, column, genome=None, parent_ids=None):
        self.Surface = Surface
        self.color = BLUE
        # Set position in game grid
        self.row = row
        self.column = column
        # Set position on the actual screen
        left = row * WIDTH
        top = column * HEIGHT
        self.Rect = [left, top, WIDTH, HEIGHT]
        # Make solid
        self.width = 0
        self.generation = 0
        self.genome = genome
        self.parent_ids = parent_ids

