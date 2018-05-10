import pygame
import random
import csv
import argparse

from food import Food
from organism import Organism

BLACK = 0, 0, 0

history = {}


def main(grid_size, initial_food_rate, initial_organism_rate, data_output_location, gui):
    # Create the game grid
    game_grid = create_game_grid(grid_size)
    # Add food
    game_grid = randomly_add_food(game_grid, initial_food_rate)
    # Add organisms
    game_grid = randomly_add_organisms(game_grid, initial_organism_rate)

    if gui:
        pygame.init()
        size = width, height = grid_size * 10, grid_size * 10
        screen = pygame.display.set_mode(size)

    done = False
    steps = 0

    while not done:
        if gui:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

        # Let all organisms do one action
        game_grid = organism_action_step(game_grid)

        # Check if all of the organisms are dead
        if organisms_left(game_grid) == 0:
            print("All organisms are dead after " + str(steps) + " steps :D")
            done = True
            print("Writing out data to csv")
            write_to_csv(history, data_output_location)
        else:
            steps += 1

        if gui:
            # Draw stuff onto screen
            screen.fill(BLACK)
            draw_objects(game_grid, screen)
            # Update the screen with what has been drawn
            pygame.display.flip()

    if gui:
        pygame.quit()


def organism_action_step(game_grid):
    for row in range(len(game_grid)):
        for column in range(len(game_grid[0])):
            obj = game_grid[row][column]
            if type(obj) == Organism:
                game_grid, reward, visible_tiles, choice = obj.random_action(game_grid)
                new_record = [obj.id]
                for tile in visible_tiles:
                    new_record.append(tile)
                new_record.append(choice)
                new_record.append(reward)
                if obj.id not in history:
                    history[obj.id] = [new_record]
                else:
                    history[obj.id].append(new_record)
    return game_grid


def organisms_left(game_grid):
    count = 0
    for row in range(len(game_grid)):
        for column in range(len(game_grid[0])):
            if type(game_grid[row][column]) == Organism:
                count += 1
    return count


def create_game_grid(grid_size):
    game_grid = []
    for row in range(grid_size):
        game_grid.append([])
        for column in range(grid_size):
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


def write_to_csv(data, data_output_location):
    # Expect data format to be
    # {
    #   'id': [[(visible tiles), 'action taken', 'reward that step (difference between energy before/after)']]
    # }
    history_to_write = []
    for organism in data:
        for row in data[organism]:
            history_to_write.append(row)
    with open(data_output_location, 'a', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerows(history_to_write)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--games", help="Number of games to play in a row", type=int, default=1)
    parser.add_argument("--grid-size", help="The grid size", type=int, default=100)
    parser.add_argument("--initial-food-spawn", help="The initial food spawn food rate", type=float, default=0.2)
    parser.add_argument("--initial-organism-spawn", help="The initial organism spawn rate", type=float, default=0.02)
    parser.add_argument("--data-output-location", help="Where to output the recorded data", default="data/life.csv")
    parser.add_argument("--no-gui", help="Don't render any GUI elements. Useful for quick data collection", action="store_true")
    args = parser.parse_args()
    for i in range(args.games):
        main(args.grid_size, args.initial_food_spawn, args.initial_organism_spawn, args.data_output_location, not args.no_gui)

