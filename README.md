# Game of Life


2 dimensional grid

Objects:

- Organisms
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

- Food particles
  - Static
  - Randomly placed throughout the world and slowly regenerated
    - How does differing the rate of regeneration change behavior?

### How to Run

```
python main.py
```


#### TODOs

- Store large log of initial memory and train new organisms models on it before continuing
- Replay with a GUI given a log file (Useful for training w/o GUI and then viewing it later)
- Create model based off genome
- Reproduction using genomes

