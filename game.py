import pygame
import random
import copy

from food import Food
from organism import Organism

BLACK = 0, 0, 0
GAME_GRID_SIZE = 100
ADD_FOOD_PROBABILITY = 0.2
ADD_ORGANISM_PROBABILITY = 0.01


def main():
    pygame.init()

    # Create the game grid
    game_grid = create_game_grid()

    size = width, height = GAME_GRID_SIZE * 10, GAME_GRID_SIZE * 10
    screen = pygame.display.set_mode(size)
    done = False

    # Add food
    game_grid = randomly_add_food(game_grid, ADD_FOOD_PROBABILITY)

    # Add organisms
    game_grid = randomly_add_organisms(game_grid, ADD_ORGANISM_PROBABILITY)

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        screen.fill(BLACK)

        # Let all organisms do one action
        game_grid = organism_action_step(game_grid)

        # Draw stuff onto screen
        draw_objects(game_grid, screen)

        # Update the screen with what has been drawn
        pygame.display.flip()

    pygame.quit()


def organism_action_step(game_grid):
    for row in range(len(game_grid)):
        for column in range(len(game_grid[0])):
            obj = game_grid[row][column]
            if type(obj) == Organism:
                game_grid = obj.random_action(game_grid)
    return game_grid


def create_game_grid():
    game_grid = []
    for row in range(GAME_GRID_SIZE):
        game_grid.append([])
        for column in range(GAME_GRID_SIZE):
            game_grid[row].append(None)
    return game_grid


def randomly_add_food(game_grid, probability):
    for row in range(len(game_grid)):
        for column in range(len(game_grid[row])):
            if decision(probability):
                game_grid[row][column] = Food(row, column)
    return game_grid


def randomly_add_organisms(game_grid, probability):
    for row in range(len(game_grid)):
        for column in range(len(game_grid[row])):
            if decision(probability):
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


def decision(probability):
    return random.random() < probability


if __name__ == '__main__':
    main()
