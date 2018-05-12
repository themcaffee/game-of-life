# Game of Life

Simulates a small world with organisms that can eat food, eat eachother,
and make offspring. Decisions of the organisms are based off a neural network
based on the genome of the organism. The genome corresponds to the hyperparameters
of the network.


### How to Run

```
python game.py
```

### Get argument options

```
python game.py -h
```

### Generate training data

```
python game.py --random --store-data --no-gui --games=15 --no-memory-read
```

### Play using genomes + neural networks and then replay it after

```
python game.py --max-ids-to-read=50 --no-gui --store-history
python play_game_log.py -i data/history_log.csv -a data/history_arguments.csv
```

### Basic game info

#### Organisms

- Have genome that dictates behavior and traits
- Can either eat food particles or other creatures
- Can mate with other organisms and produce offspring if in adjacent tile
- Starts off with X amount of energy
- Has X amount of maximum amount of energy
- Gain energy by eating food particles or organism
- Each turn expends 1 energy
- Actions:
    - Move
      - Can move north, east, south, or west
    - Eat
      - Can eat a food particle if adjacent tile (X amount of energy)
      - Can eat another organism if adjacent tile (X amount of energy)
    - Mate
      - Can mate with another organism if adjacent tile
      - Spawns a baby organism with the combined genome of the parents
      - Baby placed randomly on map

#### Food particles
- Static
- Randomly placed throughout the world and slowly regenerated
- How does differing the rate of regeneration change behavior?


#### TODOs

- Better storage of history log + arguments and allow for different naming schema

