GREEN = (0, 255, 0)


class Food:
    def __init__(self, row, column):
        self.color = GREEN
        self.width = 10
        self.height = 10
        # Set position in grid
        self.row = row
        self.column = column
        # Calculate and set position on screen
        left = row * self.width
        top = column * self.height
        self.rect = [left, top, self.width, self.height]
