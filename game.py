import pygame

from food import Food

BLACK = 0, 0, 0
GAME_GRID_SIZE = 20


def main():
    pygame.init()

    # Create the game grid
    game_grid = []
    for row in range(GAME_GRID_SIZE):
        game_grid.append([])
        for column in range(GAME_GRID_SIZE):
            game_grid[row].append(None)

    size = width, height = 240, 240
    screen = pygame.display.set_mode(size)
    done = False

    # Add food
    for row in range(len(game_grid)):
        for column in range(len(game_grid[row])):
            game_grid[row][column] = Food(screen, row, column)

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        screen.fill(BLACK)

        # Update the screen with what has been drawn
        pygame.display.flip()

    pygame.quit()

