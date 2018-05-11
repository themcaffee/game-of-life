FOOD_COLOR = (0, 255, 0)
FOOD_WIDTH = 10
FOOD_HEIGHT = 10


class Food:
    def __init__(self, row, column):
        self.color = FOOD_COLOR
        self.width = FOOD_WIDTH
        self.height = FOOD_HEIGHT
        # Set position in grid
        self.row = row
        self.column = column
        # Calculate and set position on screen
        left = row * self.width
        top = column * self.height
        self.rect = [left, top, self.width, self.height]
