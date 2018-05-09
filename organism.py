import pygame


BLUE = (0, 0, 255)


class Organism:
    def __init__(self, row, column, genome=None, parent_ids=None):
        self.color = BLUE
        self.width = 10
        self.height = 10
        # Set position in game grid
        self.row = row
        self.column = column
        # Set position on the actual screen
        left = row * self.width
        top = column * self.height
        self.rect = [left, top, self.width, self.height]
        # Make solid
        self.generation = 0
        self.genome = genome
        self.parent_ids = parent_ids

