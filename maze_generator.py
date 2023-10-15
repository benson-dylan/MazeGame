import numpy as np

from constants import *

def generate_maze(close_exit_to_player=True):
    maze = np.random.choice([0, 0, 0, 0, 1, 1], (MAP_SIZE, MAP_SIZE))
    maze[0, :], maze[MAP_SIZE-1, :], maze[:, 0], maze[:, MAP_SIZE-1] = (1, 1, 1, 1)

    player_x, player_y, player_rotation = 1.5, np.random.randint(1, MAP_SIZE - 1) + .5, np.pi / 4
    x, y = int(player_x), int(player_y)
    maze[x][y] = 0
    count = 0

    while True:
        test_x, test_y = (x, y)

        if np.random.uniform() > 0.5:
            test_x = test_x + np.random.choice([-1, 1])
        else:
            test_y = test_y + np.random.choice([-1, 1])

        if test_x > 0 and test_x < MAP_SIZE - 1 and test_y > 0 and test_y < MAP_SIZE - 1:
            if maze[test_x][test_y] == 0 or count > 5:
                count = 0
                x, y = (test_x, test_y)
                maze[x][y] = 0

                if x == MAP_SIZE - 2:
                    if close_exit_to_player:
                        # Place exit closer to the player
                        exit_x, exit_y = (x, y)
                    else:
                        # Place exit randomly
                        exit_x, exit_y = np.random.randint(1, MAP_SIZE - 1), np.random.randint(1, MAP_SIZE - 1)
                    break
            else:
                count = count + 1

    return player_x, player_y, player_rotation, maze, exit_x, exit_y

