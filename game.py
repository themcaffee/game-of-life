import pygame
import random
import csv

from food import Food
from organism import Organism

BLACK = 0, 0, 0
GAME_GRID_SIZE = 100
ADD_FOOD_PROBABILITY = 0.2
ADD_ORGANISM_PROBABILITY = 0.02
GAMES_TO_PLAY = 2


history = []


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

    steps = 0

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        screen.fill(BLACK)

        # Let all organisms do one action
        game_grid = organism_action_step(game_grid)

        # Check if all of the organisms are dead
        if organisms_left(game_grid) == 0:
            print("All organisms are dead after " + str(steps) + " steps :D")
            done = True
            print("Writing out data to csv")
            write_to_csv(history)
        else:
            steps += 1

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
                game_grid, energy, visible_tiles, choice = obj.random_action(game_grid)
                history.append([visible_tiles[0], visible_tiles[1], visible_tiles[2], visible_tiles[3], visible_tiles[4], visible_tiles[5], visible_tiles[6], visible_tiles[7], choice, energy])
    return game_grid


def organisms_left(game_grid):
    count = 0
    for row in range(len(game_grid)):
        for column in range(len(game_grid[0])):
            if type(game_grid[row][column]) == Organism:
                count += 1
    return count


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


def write_to_csv(data):
    # Expect data format to be
    # [
    #   ['Top value', 'Top Left Value', 'Left value', 'Bottom left value', 'bottom value', 'bottom right value', 'Right value', 'top right value', 'action taken', 'reward that step (difference between energy before/after)']
    # ]
    with open('data/life.csv', 'a', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerows(data)


if __name__ == '__main__':
    for i in range(GAMES_TO_PLAY):
        main()

