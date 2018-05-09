import pygame
import random

from food import Food
from organism import Organism

BLACK = 0, 0, 0
GAME_GRID_SIZE = 100


def main():
    pygame.init()

    # Create the game grid
    game_grid = create_game_grid()

    size = width, height = GAME_GRID_SIZE * 10, GAME_GRID_SIZE * 10
    screen = pygame.display.set_mode(size)
    done = False

    # Add food
    game_grid = randomly_add_food(game_grid)

    # Add organisms
    game_grid = randomly_add_organisms(game_grid)

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        screen.fill(BLACK)

        # Draw stuff onto screen
        draw_objects(game_grid, screen)

        # Update the screen with what has been drawn
        pygame.display.flip()

    pygame.quit()


def create_game_grid():
    game_grid = []
    for row in range(GAME_GRID_SIZE):
        game_grid.append([])
        for column in range(GAME_GRID_SIZE):
            game_grid[row].append(None)
    return game_grid


def randomly_add_food(game_grid):
    for row in range(len(game_grid)):
        for column in range(len(game_grid[row])):
            if bool(random.getrandbits(1)):
                game_grid[row][column] = Food(row, column)
    return game_grid


def randomly_add_organisms(game_grid):
    for row in range(len(game_grid)):
        for column in range(len(game_grid[row])):
            if bool(random.getrandbits(1)):
                game_grid[row][column] = Organism(row, column)
    return game_grid


def draw_objects(game_grid, screen):
    for row in range(len(game_grid)):
        for column in range(len(game_grid[row])):
            obj = game_grid[row][column]
            if type(obj) == Food:
                pygame.draw.rect(screen, obj.color, obj.rect)
            elif type(obj) == Organism:
                pygame.draw.rect(screen, obj.color, obj.rect)


if __name__ == '__main__':
    main()
