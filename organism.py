import uuid

from food import Food
import numpy as np

BLUE = (0, 0, 255)
INITIAL_ENERGY = 100
MAX_ENERGY = 200
ENERGY_FROM_EATING = 50
ATTEMPT_LIMIT = 50
ENERGY_FROM_MOVING = -1
ENERGY_FROM_MATING = -1
# Rewards for model
REWARD_FROM_EATING = 100
REWARD_FROM_MOVING = -1
REWARD_FROM_MATING = 50


class Organism:
    def __init__(self, row, column, genome=None, parent_ids=None):
        self.id = str(uuid.uuid4())
        self.color = BLUE
        self.width = 10
        self.height = 10
        # Set position in game grid
        self._set_position(row, column)
        # Make solid
        self.generation = 0
        self.genome = genome
        self.parent_ids = parent_ids
        self.energy = INITIAL_ENERGY

    def _get_visible_tiles(self, game_grid):
        visible = []
        for row_change in range(-2, 2):
            for col_change in range(-2, 2):
                if row_change == 0 and col_change == 0:
                    continue
                elif self._out_of_bounds(game_grid, self.row + row_change, self.column + col_change):
                    visible.append(-1)
                else:
                    visible.append(self._convert_obj_to_int_mapping(game_grid[self.row + row_change][self.column + col_change]))
        return visible

    def _convert_obj_to_int_mapping(self, obj):
        if obj == -1:
            return -1
        elif not obj:
            return 0
        elif type(obj) == Organism:
            return 1
        elif type(obj) == Food:
            return 2
        else:
            return obj

    def _out_of_bounds(self, game_grid, row, column):
        if column < 0:
            return True
        elif row < 0:
            return True
        elif len(game_grid) - 1 < row:
            return True
        elif len(game_grid[0]) - 1 < column:
            return True
        else:
            return False

    def _die(self, game_grid):
        game_grid[self.row][self.column] = None

    def _set_position(self, row, column):
        self.row = row
        self.column = column
        left = row * self.width
        top = column * self.height
        self.rect = [left, top, self.width, self.height]

    def _move_to(self, game_grid, row, column):
        if self._out_of_bounds(game_grid, row, column):
            return False
        elif game_grid[row][column]:
            return False

        self.energy += ENERGY_FROM_MOVING
        if self.energy <= 0:
            return self._die(game_grid)

        game_grid[self.row][self.column] = None
        game_grid[row][column] = self
        self._set_position(row, column)
        return game_grid

    def move_up(self, game_grid):
        return self._move_to(game_grid, self.row, self.column - 1)

    def move_left(self, game_grid):
        return self._move_to(game_grid, self.row - 1, self.column)

    def move_right(self, game_grid):
        return self._move_to(game_grid, self.row + 1, self.column)

    def move_down(self, game_grid):
        return self._move_to(game_grid, self.row, self.column + 1)

    def _eat(self, game_grid, row, column):
        if self._out_of_bounds(game_grid, row, column):
            return False
        elif not game_grid[row][column]:
            return False

        self.energy += ENERGY_FROM_EATING
        if self.energy > MAX_ENERGY:
            self.energy = MAX_ENERGY

        game_grid[row][column] = None
        return game_grid

    def eat_up(self, game_grid):
        return self._eat(game_grid, self.row, self.column - 1)

    def eat_left(self, game_grid):
        return self._eat(game_grid, self.row - 1, self.column)

    def eat_right(self, game_grid):
        return self._eat(game_grid, self.row + 1, self.column)

    def eat_down(self, game_grid):
        return self._eat(game_grid, self.row, self.column + 1)

    def _mate(self, game_grid, row, column):
        if self._out_of_bounds(game_grid, row, column):
            return False
        elif type(game_grid[row][column]) != Organism:
            return False
        self.energy += ENERGY_FROM_MATING
        if self.energy <= 0:
            return self._die(game_grid)

        # Random placement of baby
        searching = True
        while searching:
            random_row = np.random.randint(0, len(game_grid))
            random_col = np.random.randint(0, len(game_grid[0]))
            if not game_grid[random_row][random_col]:
                game_grid[random_row][random_col] = Organism(random_row, random_col)
                searching = False
        return game_grid

    def mate_up(self, game_grid):
        return self._mate(game_grid, self.row, self.column - 1)

    def mate_left(self, game_grid):
        return self._mate(game_grid, self.row - 1, self.column)

    def mate_right(self, game_grid):
        return self._mate(game_grid, self.row + 1, self.column)

    def mate_down(self, game_grid):
        return self._mate(game_grid, self.row, self.column + 1)

    def do_nothing(self, game_grid):
        return game_grid

    def random_action(self, game_grid):
        attempt = 0
        visible_tiles = self._get_visible_tiles(game_grid)
        reward = 0
        choice = 12
        while attempt <= ATTEMPT_LIMIT:
            choice = np.random.randint(0, 12)
            if choice == 0:
                new_grid = self.move_up(game_grid)
                energy = ENERGY_FROM_MOVING
            elif choice == 1:
                new_grid = self.move_left(game_grid)
                energy = ENERGY_FROM_MOVING
            elif choice == 2:
                new_grid = self.move_right(game_grid)
                energy = ENERGY_FROM_MOVING
            elif choice == 3:
                new_grid = self.move_down(game_grid)
                energy = ENERGY_FROM_MOVING
            elif choice == 4:
                new_grid = self.eat_up(game_grid)
                energy = ENERGY_FROM_EATING
            elif choice == 5:
                new_grid = self.eat_left(game_grid)
                energy = ENERGY_FROM_EATING
            elif choice == 6:
                new_grid = self.eat_right(game_grid)
                energy = ENERGY_FROM_EATING
            elif choice == 7:
                new_grid = self.eat_down(game_grid)
                energy = ENERGY_FROM_EATING
            elif choice == 8:
                new_grid = self.mate_up(game_grid)
                energy = ENERGY_FROM_MATING
            elif choice == 9:
                new_grid = self.mate_left(game_grid)
                energy = ENERGY_FROM_MATING
            elif choice == 10:
                new_grid = self.mate_right(game_grid)
                energy = ENERGY_FROM_MATING
            elif choice == 11:
                new_grid = self.mate_down(game_grid)
                energy = ENERGY_FROM_MATING
            elif choice == 12:
                new_grid = self.do_nothing(game_grid)
                energy = 0

            if choice == 0 or choice == 1 or choice == 2 or choice == 3:
                reward = REWARD_FROM_MOVING
            elif choice == 4 or choice == 5 or choice == 6 or choice == 7:
                reward = REWARD_FROM_EATING
            elif choice == 8 or choice == 9 or choice == 10 or choice == 11:
                reward = REWARD_FROM_MATING
            else:
                reward = 0

            if new_grid:
                return new_grid, reward, visible_tiles, choice
            else:
                attempt += 1
        return self.do_nothing(game_grid), reward, visible_tiles, choice



