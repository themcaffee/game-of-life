import argparse
import sys
import csv
import pygame
import ast

from food import FOOD_COLOR, FOOD_WIDTH, FOOD_HEIGHT
from game import SCREEN_BACKGROUND
from organism import ORGANISM_WIDTH, ORGANISM_HEIGHT, ORGANISM_COLOR


FRAME_RATE = 30


def main(arguments_file, input_file):
    grid_size, initial_food_rate, initial_organism_rate, random, memory_read, max_ids_to_read = read_argument_file(arguments_file)
    game_states = read_game_states(input_file)

    pygame.init()
    size = width, height = grid_size * 10, grid_size * 10
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()

    print("Starting game sim")
    print(str(len(game_states)))
    for state in game_states:
        clock.tick(FRAME_RATE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.fill(SCREEN_BACKGROUND)
        draw_objects(state, screen)
        pygame.display.flip()

    pygame.quit()


def draw_objects(game_state, screen):
    for row in range(len(game_state) - 1):
        for column in range(len(game_state[0]) - 1):
            obj = game_state[row][column]
            if obj == 1:
                food_rect = [row * FOOD_WIDTH, column * FOOD_HEIGHT, FOOD_WIDTH, FOOD_HEIGHT]
                pygame.draw.rect(screen, FOOD_COLOR, food_rect)
            elif obj == 2:
                organism_rect = [row * ORGANISM_WIDTH, column * ORGANISM_HEIGHT, ORGANISM_WIDTH, ORGANISM_HEIGHT]
                pygame.draw.rect(screen, ORGANISM_COLOR, organism_rect)


def read_game_states(input_file):
    print("Reading in game states")
    game_states = []
    with open(input_file, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar="|")
        for state in reader:
            converted_state = []
            for row in state:
                converted_row = ast.literal_eval(row)
                converted_state.append(converted_row)
            game_states.append(converted_state)
    return game_states


def read_argument_file(arguments_file):
    with open(arguments_file, newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar="|")
        for row in reader:
            grid_size = int(row[0])
            initial_food_rate = float(row[1])
            initial_organism_rate = float(row[2])
            random = bool(row[3])
            memory_read = bool(row[4])
            max_ids_to_read = int(row[5])
    return grid_size, initial_food_rate, initial_organism_rate, random, memory_read, max_ids_to_read


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-file", help="States log file to replay")
    parser.add_argument("-a", "--arg-file", help="File with arguments of game")
    args = parser.parse_args()
    main(args.arg_file, args.input_file)