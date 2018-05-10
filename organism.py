from pprint import pprint
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
REWARD_FROM_DYING = -1000


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
        self.alive = True

    def _get_visible_tiles(self, game_grid, organism_row=None, organism_column=None):
        if not organism_row:
            organism_row = self.row
        if not organism_column:
            organism_column = self.column

        visible = []
        for row_change in range(-2, 2):
            for col_change in range(-2, 2):
                if row_change == 0 and col_change == 0:
                    continue
                elif self._out_of_bounds(game_grid, organism_row + row_change, organism_column + col_change):
                    visible.append(-1)
                else:
                    visible.append(self._convert_obj_to_int_mapping(game_grid[organism_row + row_change][organism_column + col_change]))
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
        self.alive = False
        game_grid[self.row][self.column] = None
        return game_grid

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

    def _eat(self, game_grid, row, column, history):
        if self._out_of_bounds(game_grid, row, column):
            return False, history
        elif not game_grid[row][column]:
            return False, history

        self.energy += ENERGY_FROM_EATING
        if self.energy > MAX_ENERGY:
            self.energy = MAX_ENERGY

        if type(game_grid[row][column]) == Organism:
            # Record the dead organism's last reward as dying
            dead_organism = game_grid[row][column]
            if dead_organism.id in history:
                history[dead_organism.id][-1][-1] = REWARD_FROM_DYING
        game_grid[row][column] = None
        return game_grid, history

    def eat_up(self, game_grid, history):
        return self._eat(game_grid, self.row, self.column - 1, history)

    def eat_left(self, game_grid, history):
        return self._eat(game_grid, self.row - 1, self.column, history)

    def eat_right(self, game_grid, history):
        return self._eat(game_grid, self.row + 1, self.column, history)

    def eat_down(self, game_grid, history):
        return self._eat(game_grid, self.row, self.column + 1, history)

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
            random_row = np.random.randint(0, len(game_grid) - 1)
            random_col = np.random.randint(0, len(game_grid[0]) - 1)
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

    def _add_to_history(self, history, visible_tiles, choice, reward, id=None):
        if not id:
            id = self.id
        new_record = [id]
        for tiles in visible_tiles:
            new_record.append(tiles)
        new_record.append(choice)
        new_record.append(reward)
        if id not in history:
            history[id] = [new_record]
        else:
            history[id].append(new_record)
        return history

    def random_action(self, game_grid, history):
        attempt = 0
        visible_tiles = self._get_visible_tiles(game_grid)
        reward = 0
        choice = 12
        while attempt <= ATTEMPT_LIMIT:
            choice = np.random.randint(0, 12)
            if choice == 0:
                new_grid = self.move_up(game_grid)
            elif choice == 1:
                new_grid = self.move_left(game_grid)
            elif choice == 2:
                new_grid = self.move_right(game_grid)
            elif choice == 3:
                new_grid = self.move_down(game_grid)
            elif choice == 4:
                new_grid, history = self.eat_up(game_grid, history)
            elif choice == 5:
                new_grid, history = self.eat_left(game_grid, history)
            elif choice == 6:
                new_grid, history = self.eat_right(game_grid, history)
            elif choice == 7:
                new_grid, history = self.eat_down(game_grid, history)
            elif choice == 8:
                new_grid = self.mate_up(game_grid)
            elif choice == 9:
                new_grid = self.mate_left(game_grid)
            elif choice == 10:
                new_grid = self.mate_right(game_grid)
            elif choice == 11:
                new_grid = self.mate_down(game_grid)
            elif choice == 12:
                new_grid = self.do_nothing(game_grid)

            if not self.alive:
                reward = REWARD_FROM_DYING
            elif choice == 0 or choice == 1 or choice == 2 or choice == 3:
                reward = REWARD_FROM_MOVING
            elif choice == 4 or choice == 5 or choice == 6 or choice == 7:
                reward = REWARD_FROM_EATING
            elif choice == 8 or choice == 9 or choice == 10 or choice == 11:
                reward = REWARD_FROM_MATING
            else:
                reward = 0

            if new_grid:
                history = self._add_to_history(history, visible_tiles, choice, reward)
                return new_grid, history
            else:
                attempt += 1
        history = self._add_to_history(history, visible_tiles, choice, reward)
        return self.do_nothing(game_grid), history



