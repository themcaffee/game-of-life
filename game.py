import pygame
import random

from food import Food
from organism import Organism

BLACK = 0, 0, 0
GAME_GRID_SIZE = 100


def main():
    pygame.init()

    # Create the game grid
    game_grid = []
    for row in range(GAME_GRID_SIZE):
        game_grid.append([])
        for column in range(GAME_GRID_SIZE):
            game_grid[row].append(None)

    size = width, height = GAME_GRID_SIZE * 10, GAME_GRID_SIZE * 10
    screen = pygame.display.set_mode(size)
    done = False

    # Add food
    for row in range(len(game_grid)):
        for column in range(len(game_grid[row])):
            if bool(random.getrandbits(1)):
                game_grid[row][column] = Food(row, column)

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        screen.fill(BLACK)

        # Draw food
        for row in range(len(game_grid)):
            for column in range(len(game_grid[row])):
               obj = game_grid[row][column]
               if type(obj) == Food:
                   pygame.draw.rect(screen, obj.color, obj.rect)
               elif type(obj) == Organism:
                   pygame.draw.rect(screen, obj.color, obj.rect)

        # Update the screen with what has been drawn
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
