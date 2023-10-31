import numpy as np

from constants import *

def generate_maze(close_exit_to_player=True):
    # Generate a random maze layout with 1s (walls) and 0s (open paths)
    maze = np.random.choice([0, 0, 0, 0, 1, 1], (MAP_SIZE, MAP_SIZE))
    # Ensure the maze's border is surrounded by walls
    maze[0, :], maze[MAP_SIZE-1, :], maze[:, 0], maze[:, MAP_SIZE-1] = (1, 1, 1, 1)

    # Initialize the player's position and orientation
    player_x, player_y, player_rotation = 1.5, np.random.randint(1, MAP_SIZE - 1) + .5, np.pi / 4
    x, y = int(player_x), int(player_y)
    
    # Mark the player's initial position as open
    maze[x][y] = 0
    count = 0

    # Find a valid location for the exit and pace it
    while True:
        # Create test coordinates based on current player (x, y) values
        test_x, test_y = (x, y)

        # Randomly decide to move in the x or y direction
        if np.random.uniform() > 0.5:
            test_x = test_x + np.random.choice([-1, 1])
        else:
            test_y = test_y + np.random.choice([-1, 1])

        # Check if the test coordinates are within the maze boundaries
        if test_x > 0 and test_x < MAP_SIZE - 1 and test_y > 0 and test_y < MAP_SIZE - 1:
            # Check if the test cell is open (0)
            if maze[test_x][test_y] == 0 or count > 5:
                count = 0
                x, y = (test_x, test_y)
                maze[x][y] = 0

                # Find a valid second-to-last column of the maze
                if x == MAP_SIZE - 2:
                    if close_exit_to_player:
                        # Place exit closer to the player, (easier to find)
                        exit_x, exit_y = (x, y)
                    else:
                        # Place exit randomly
                        exit_x, exit_y = np.random.randint(1, MAP_SIZE - 1), np.random.randint(1, MAP_SIZE - 1)
                    break
            else:
                count = count + 1

    return player_x, player_y, player_rotation, maze, exit_x, exit_y

