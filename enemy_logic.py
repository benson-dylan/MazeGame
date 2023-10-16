import numpy as np
from numba import njit

from constants import *

@njit()
def update_enemies(player_x, player_y, player_rotation, enemies, maze, elapsed_time):
    for enemy in range(len(enemies)):
        # Calculate the new position based on enemy movement
        cos, sin = elapsed_time * np.cos(enemies[enemy][6]), elapsed_time * np.sin(enemies[enemy][6])
        new_x, new_y = enemies[enemy][0] + cos, enemies[enemy][1] + sin

        # Check for wall collisions using the map data
        wall_collision = False
        for dx in [-0.1, 0.1]:
            for dy in [-0.1, 0.1]:
                if maze[int(new_x + dx) % (MAP_SIZE - 1)][int(new_y + dy) % (MAP_SIZE - 1)]:
                    wall_collision = True
                    break

        if wall_collision:
            # When AI hits the wall, they will change direction
            new_x, new_y = enemies[enemy][0], enemies[enemy][1]
            enemies[enemy][6] = enemies[enemy][6] + np.random.uniform(-0.5, 0.5)
        else:
            enemies[enemy][0], enemies[enemy][1] = new_x, new_y

        # Calculate the angle and direction relative to the player
        angle = np.arctan2(new_y - player_y, new_x - player_x)
        if abs(player_x + np.cos(angle) - new_x) > abs(player_x - new_x):
            angle = (angle - np.pi) % (2 * np.pi)

        angle_difference = (player_rotation - angle) % (2 * np.pi)

        if angle_difference > 10.5 * np.pi / 6 or angle_difference < 1.5 * np.pi / 6:
            # Calculate direction and other properties
            direction_to_player = ((enemies[enemy][6] - angle - 3 * np.pi / 4) % (2 * np.pi)) / (np.pi / 2)
            enemies[enemy][2] = angle_difference
            enemies[enemy][7] = direction_to_player
            enemies[enemy][3] = 1 / np.sqrt((new_x - player_x) ** 2 + (new_y - player_y) ** 2 + 1e-16)

            # Check for wall collisions along the path to the player
            cos, sin = (player_x - new_x) * enemies[enemy][3], (player_y - new_y) * enemies[enemy][3]
            x, y = new_x, new_y
            for i in range(int((1 / enemies[enemy][3]) / 0.05)):
                x, y = x + 0.05 * cos, y + 0.05 * sin
                if (maze[int(x - 0.02 * cos) % (MAP_SIZE - 1)][int(y) % (MAP_SIZE - 1)] or
                    maze[int(x) % (MAP_SIZE - 1)][int(y - 0.02 * sin) % (MAP_SIZE - 1)]):
                    enemies[enemy][3] = 9999
                    break
        else:
            enemies[enemy][3] = 9999

    # Sort the enemies by distance to the player
    enemies = enemies[enemies[:, 3].argsort()]
    return enemies

def spawn_enemies(num_enemies_to_spawn, maze):
    enemies = []
    while len(enemies) < num_enemies_to_spawn:
        # Randomly select initial coordinates for an enemy within the maze
        x, y = np.random.uniform(1, MAP_SIZE - 2), np.random.uniform(1, MAP_SIZE - 2)

        # Make sure that the selected position is not blocked by maze walls
        if not any(maze[int(x + dx) % (MAP_SIZE - 1)][int(y + dy) % (MAP_SIZE - 1)] for dx in [-0.1, 0.1] for dy in [-0.1, 0.1]):
            # Initialize enemy attributes
            angle_to_player, inverse_distance_to_player, direction_to_player = 0, 0, 0
            entype = np.random.choice([0, 1])  # 0 zombie, 1 skeleton
            direction = np.random.uniform(0, 2 * np.pi)  # facing direction
            map_location = np.random.uniform(7, 10)
            enemies.append([x, y, angle_to_player, inverse_distance_to_player, entype, map_location, direction, direction_to_player])

    return np.asarray(enemies)

