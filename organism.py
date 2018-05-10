import uuid
import numpy as np
import random
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

from food import Food

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
BATCH_SIZE = 32


class Organism:
    def __init__(self, row, column, state_size=24, action_size=13, genome=None, parent_ids=None, memories=None):
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

        # DQN Stuff
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95    # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()
        self.past_memories = memories
        if self.past_memories:
            self.train_from_initial(self.past_memories)

    def _get_visible_tiles(self, game_grid, organism_row=None, organism_column=None):
        if not organism_row:
            organism_row = self.row
        if not organism_column:
            organism_column = self.column

        visible = []
        for row_change in range(-2, 3):
            for col_change in range(-2, 3):
                if row_change == 0 and col_change == 0:
                    continue
                elif self._out_of_bounds(game_grid, organism_row + row_change, organism_column + col_change):
                    visible.append(-1)
                else:
                    visible.append(self._convert_obj_to_int_mapping(game_grid[organism_row + row_change][organism_column + col_change]))
        numpy_visible = np.array(visible).reshape((1, 24))
        return numpy_visible

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
            random_row = np.random.randint(0, len(game_grid) - 1)
            random_col = np.random.randint(0, len(game_grid[0]) - 1)
            if not game_grid[random_row][random_col]:
                game_grid[random_row][random_col] = Organism(random_row, random_col, memories=self.past_memories)
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
        while attempt <= ATTEMPT_LIMIT:
            random_choice = np.random.randint(0, 12)
            new_grid, reward = self._do_action(game_grid, random_choice)
            if new_grid:
                done = reward == REWARD_FROM_DYING
                new_visible_tiles = self._get_visible_tiles(new_grid)
                self.remember(visible_tiles, random_choice, reward, new_visible_tiles, done)
                return new_grid, reward
            else:
                attempt += 1
        self.remember(visible_tiles, 12, reward, visible_tiles, False)
        return self.do_nothing(game_grid), reward

    def _do_action(self, game_grid, action):
        new_grid = False
        if action == 0:
            new_grid = self.move_up(game_grid)
        elif action == 1:
            new_grid = self.move_left(game_grid)
        elif action == 2:
            new_grid = self.move_right(game_grid)
        elif action == 3:
            new_grid = self.move_down(game_grid)
        elif action == 4:
            new_grid = self.eat_up(game_grid)
        elif action == 5:
            new_grid = self.eat_left(game_grid)
        elif action == 6:
            new_grid = self.eat_right(game_grid)
        elif action == 7:
            new_grid = self.eat_down(game_grid)
        elif action == 8:
            new_grid = self.mate_up(game_grid)
        elif action == 9:
            new_grid = self.mate_left(game_grid)
        elif action == 10:
            new_grid = self.mate_right(game_grid)
        elif action == 11:
            new_grid = self.mate_down(game_grid)
        elif action == 12:
            new_grid = self.do_nothing(game_grid)

        if not self.alive:
            reward = REWARD_FROM_DYING
        elif action == 0 or action == 1 or action == 2 or action == 3:
            reward = REWARD_FROM_MOVING
        elif action == 4 or action == 5 or action == 6 or action == 7:
            reward = REWARD_FROM_EATING
        elif action == 8 or action == 9 or action == 10 or action == 11:
            reward = REWARD_FROM_MATING
        else:
            reward = 0

        return new_grid, reward

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse',
                      optimizer=Adam(lr=self.learning_rate))
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act_from_prediction(self, state):
        if np.random.rand() <= self.epsilon:
            print("Random action for " + str(self.id))
            new_state, reward = self.random_action(state)
            return new_state

        visible_tiles = self._get_visible_tiles(state)
        act_values = self.model.predict(visible_tiles)
        # Do the action with the highest value that is possible
        sorted_actions = np.argsort(act_values[0])
        print("Predicted action for " + str(self.id))
        for action in sorted_actions:
            new_state, reward = self._do_action(state, action)
            if new_state:
                new_visible_tiles = self._get_visible_tiles(new_state)
                done = reward == REWARD_FROM_DYING
                self.remember(visible_tiles, action, reward, new_visible_tiles, done)
                return new_state

    def act(self, state):
        new_state = self.act_from_prediction(state)
        return new_state

    def replay(self, memory=None, batch_size=BATCH_SIZE):
        if not memory:
            print("Replaying for " + str(self.id))
            memory = self.memory

        if len(memory) < batch_size:
            return

        minibatch = random.sample(memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * \
                                  np.amax(self.model.predict(next_state)[0])
            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def train_from_initial(self, memories, batch_size=BATCH_SIZE):
        print("Training initial data for " + str(self.id))
        for organism_memory in memories:
            self.replay(memories[organism_memory], batch_size)
