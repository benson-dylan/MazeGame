import numpy as np

from constants import *

def generate_maze():
    map_height = np.random.choice([0, 0, 0, 0, 1, 1], (MAP_SIZE, MAP_SIZE))
    map_height[0, :], map_height[MAP_SIZE-1, :], map_height[:, 0], map_height[:, MAP_SIZE-1] = (1, 1, 1, 1)

    player_x, player_y, player_rotation = 1.5, np.random.randint(1, MAP_SIZE - 1) + .5, np.pi / 4
    x, y = int(player_x), int(player_y)
    map_height[x][y] = 0
    count = 0

    while True:
        test_x, test_y = (x, y)

        if np.random.uniform() > 0.5:
            test_x = test_x + np.random.choice([-1, 1])
        else:
            test_y = test_y + np.random.choice([-1, 1])

        if test_x > 0 and test_x < MAP_SIZE - 1 and test_y > 0 and test_y < MAP_SIZE - 1:
            if map_height[test_x][test_y] == 0 or count > 5:
                count = 0
                x, y = (test_x, test_y)
                map_height[x][y] = 0

                if x == MAP_SIZE - 2:
                    exit_x, exit_y = (x, y)
                    break
            else:
                count = count + 1

    return player_x, player_y, player_rotation, map_height, exit_x, exit_y
