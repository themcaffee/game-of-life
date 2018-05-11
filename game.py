import pygame
import random
import csv
import argparse
import numpy as np

from food import Food
from organism import Organism, BATCH_SIZE

SCREEN_BACKGROUND = 0, 0, 0
MAX_STEPS = 1000


def main(grid_size, initial_food_rate, initial_organism_rate, data_output_location, gui, games, random, store_data, memory_read, max_ids_to_read, store_history):
    # Read memories for training
    if memory_read:
        memories = read_from_csv(data_output_location, initial_food_rate, initial_organism_rate, grid_size, max_ids_to_read)
    else:
        memories = None

    for game in range(games):
        history = {}
        game_states = []

        write_game_states_arguments(grid_size, initial_food_rate, initial_organism_rate, random, memory_read, max_ids_to_read)

        # Create the game grid
        game_grid = create_game_grid(grid_size)
        # Add food
        game_grid = randomly_add_food(game_grid, initial_food_rate)
        # Add organisms
        game_grid = randomly_add_organisms(game_grid, initial_organism_rate, memories)

        if gui:
            pygame.init()
            size = width, height = grid_size * 10, grid_size * 10
            screen = pygame.display.set_mode(size)

        done = False
        steps = 0

        if store_history:
            game_states.append(game_grid)

        while not done and steps <= MAX_STEPS:
            # Let all organisms do one action
            if random:
                game_grid = organism_random_action_step(game_grid)
            else:
                game_grid = organism_predict_action_step(game_grid)

            if store_data:
                history = store_organism_data(game_grid, history)

            # Check if all of the organisms are dead
            if organisms_left(game_grid) == 0:
                print("All organisms are dead after " + str(steps) + " steps :D")
                done = True
            else:
                steps += 1

            if gui:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        done = True
                # Draw stuff onto screen
                screen.fill(SCREEN_BACKGROUND)
                draw_objects(game_grid, screen)
                # Update the screen with what has been drawn
                pygame.display.flip()

            # Append the game states to the log
            if store_history:
                game_states.append(game_grid)

        if store_data:
            write_to_csv(history, data_output_location, initial_food_rate, initial_organism_rate, grid_size)

        if store_history:
            write_game_states_log(game_states)

        if gui:
            pygame.quit()


def store_organism_data(game_grid, history):
    for row in range(len(game_grid)):
        for column in range(len(game_grid[0])):
            obj = game_grid[row][column]
            if type(obj) == Organism and len(obj.memory) > 0:
                # Get the last memory
                state, action, reward, next_state, done = obj.memory.pop()
                obj.remember(state, action, reward, next_state, done)

                # Create the new record
                visible_tiles = list(state[0])
                next_visible_tiles = list(next_state[0])
                new_record = [obj.id]
                for tile in visible_tiles:
                    new_record.append(tile)
                new_record.append(action)
                new_record.append(reward)
                for tile in next_visible_tiles:
                    new_record.append(tile)
                new_record.append(done)

                # Add new record to history
                if obj.id not in history:
                    history[obj.id] = []
                history[obj.id].append(new_record)
    return history


def organism_random_action_step(game_grid):
    for row in range(len(game_grid)):
        for column in range(len(game_grid[0])):
            obj = game_grid[row][column]
            if type(obj) == Organism:
                game_grid, _ = obj.random_action(game_grid)
    return game_grid


def organism_predict_action_step(game_grid):
    for row in range(len(game_grid)):
        for column in range(len(game_grid[0])):
            obj = game_grid[row][column]
            if type(obj) == Organism:
                game_grid = obj.act(game_grid)
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


def randomly_add_organisms(game_grid, probability, memories=None):
    for row in range(len(game_grid)):
        for column in range(len(game_grid[row])):
            if decision(probability):
                if memories:
                    organism = Organism(row, column, memories=memories)
                else:
                    organism = Organism(row, column)
                game_grid[row][column] = organism

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


def add_file_information_to_name(data_location, initial_food_spawn, initial_organism_spawn, grid_size):
    return data_location.split(".")[0] + "_" + str(initial_food_spawn) + "_" + \
               str(initial_organism_spawn) + "_" + str(grid_size) + ".csv"


def write_to_csv(data, data_output_location, initial_food_spawn, initial_organism_spawn, grid_size):
    # Expect data format to be
    # {
    #   'id': [[(visible tiles), 'action taken', 'reward that step (difference between energy before/after)']]
    # }
    history_to_write = []
    filename = add_file_information_to_name(data_output_location, initial_food_spawn, initial_organism_spawn, grid_size)
    for organism in data:
        for row in data[organism]:
            history_to_write.append(row)
    with open(filename, 'a', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerows(history_to_write)


def read_from_csv(data_location, initial_food_spawn, initial_organism_spawn, grid_size, ids_to_read):
    memories = {}
    filename = add_file_information_to_name(data_location, initial_food_spawn, initial_organism_spawn, grid_size)
    print("Reading in past memories from log for " + str(ids_to_read) + " ids")
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        id = ''
        ids_read = 0
        for row in reader:
            if id != row[0] and id != '':
                if len(memories[id]) < BATCH_SIZE:
                    memories.pop(id, None)
                    ids_read -= 1
                else:
                    ids_read += 1
            if ids_read >= ids_to_read:
                break
            id = row[0]

            if id not in memories:
                memories[id] = []
            converted_row = []
            for index in range(len(row)):
                if index == len(row) - 1:
                    converted_row.append(bool(row[index]))
                elif index == 0:
                    converted_row.append(row[index])
                else:
                    converted_row.append(int(row[index]))
            visible_tiles = np.array([converted_row[1:25]])
            action = converted_row[25]
            reward = converted_row[26]
            next_visible_tiles = np.array([converted_row[27:51]])
            done = converted_row[51]
            new_record = (visible_tiles, action, reward, next_visible_tiles, done)
            memories[id].append(new_record)
    return memories


def write_game_states_arguments(grid_size, initial_food_rate, initial_organism_rate, random,  memory_read, max_ids_to_read):
    # Record the arguments of the game
    arguments_filename = "data/history_arguments.csv"
    with open(arguments_filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL)
        game_arguments = [grid_size, initial_food_rate, initial_organism_rate, random, memory_read, max_ids_to_read]
        writer.writerow(game_arguments)


def convert_game_states_log(game_states):
    # Convert game state objects to ints
    converted_game_states = []
    for state in game_states:
        converted_game_states.append(convert_game_state(state))
    return converted_game_states


def convert_game_state(game_state):
    converted_game_state = []
    for row in range(len(game_state) - 1):
        converted_game_state.append([])
        for column in range(len(game_state[0]) - 1):
            if not game_state[row][column]:
                converted_game_state[row].append(0)
            elif type(game_state[row][column]) == Food:
                converted_game_state[row].append(1)
            elif type(game_state[row][column]) == Organism:
                converted_game_state[row].append(2)
    return converted_game_state


def write_game_states_log(game_states):
    # Record a single state of the game
    log_filename = "data/history_log.csv"
    converted_game_states = convert_game_states_log(game_states)
    with open(log_filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL)
        writer.writerows(converted_game_states)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--games", help="Number of games to play in a row", type=int, default=1)
    parser.add_argument("--grid-size", help="The grid size", type=int, default=100)
    parser.add_argument("--initial-food-spawn", help="The initial food spawn food rate", type=float, default=0.2)
    parser.add_argument("--initial-organism-spawn", help="The initial organism spawn rate", type=float, default=0.002)
    parser.add_argument("--store-data", help="Store the data in a csv", action="store_true")
    parser.add_argument("--data-output-location", help="Where to output the recorded data", default="data/life.csv")
    parser.add_argument("--no-gui", help="Don't render any GUI elements. Useful for quick data collection", action="store_true")
    parser.add_argument("--random", help="Randomly perform actions instead of prediction", action="store_true")
    parser.add_argument("--no-memory-read", help="Don't use log to train network", action="store_true")
    parser.add_argument("--max-ids-to-read", help="The maximum amount of ids to read from the log file", type=int, default=1)
    parser.add_argument("--store-history", help="Store the entire history of the game to replay it at a later time", action="store_true")
    args = parser.parse_args()
    main(args.grid_size, args.initial_food_spawn, args.initial_organism_spawn, args.data_output_location, not args.no_gui, args.games, args.random, args.store_data, not args.no_memory_read, args.max_ids_to_read, args.store_history)


