import numpy as np
from numba import njit

from constants import *

@njit()
def render_wall(x, y, maze, player_x, player_y, player_rotation, frame_buffer, wall_texture, column, cos, sin, cos2):
    # Cast a ray until it hits a wall
    step_size = 0.01
    while maze[int(x) % (MAP_SIZE - 1)][int(y) % (MAP_SIZE - 1)] == 0:
        x += step_size * cos
        y += step_size * sin

    # Calculate the height of the wall column
    distance = np.sqrt((x - player_x) ** 2 + (y - player_y) ** 2)
    height = int(HALF_VERTICAL_RESOLUTION / (distance * cos2 + 0.001))

    # Determine which part of the wall texture to use
    texture_x = int(x * 3 % 1 * 99)        
    if x % 1 < 0.02 or x % 1 > 0.98:
        texture_x = int(y * 3 % 1 * 99)

    texture_y = np.linspace(0, 3, height * 2) * 99 % 99

    # Calculate shading based on wall height
    shading = min(1.0, 0.3 + 0.7 * (height / HALF_VERTICAL_RESOLUTION))
    
    # Handle transparent walls (ash) and shading
    ash = 0
    if maze[int(x - 0.33) % (MAP_SIZE - 1)][int(y - 0.33) % (MAP_SIZE - 1)]:
        ash = 1
        
    if maze[int(x - 0.01) % (MAP_SIZE - 1)][int(y - 0.01) % (MAP_SIZE - 1)]:
        shading = shading * 0.5
        ash = 0
    
    # Render the wall texture
    color = shading
    for k in range(height * 2):
        if HALF_VERTICAL_RESOLUTION - height + k >= 0 and HALF_VERTICAL_RESOLUTION - height + k < 2 * HALF_VERTICAL_RESOLUTION:
            if ash and 1 - k / (2 * height) < 1 - texture_x / 99:
                color, ash = 0.5 * color, 0
            frame_buffer[column][HALF_VERTICAL_RESOLUTION - height + k] = color * wall_texture[texture_x][int(texture_y[k])]
            if HALF_VERTICAL_RESOLUTION + 3 * height - k < 2 * HALF_VERTICAL_RESOLUTION:
                frame_buffer[column][HALF_VERTICAL_RESOLUTION + 3 * height - k] = color * wall_texture[texture_x][int(texture_y[k])]

    # Return the frame buffer and updated x, y, height
    return frame_buffer, x, y, height

@njit()
def render_floor(x, y, height, cos2, player_x, cos, player_y, sin, frame_buffer, column, floor_texture, maze, exit_x, exit_y):
    # Render the floor and apply shading
    for row in range(HALF_VERTICAL_RESOLUTION - height):
        distance = (HALF_VERTICAL_RESOLUTION / (HALF_VERTICAL_RESOLUTION - row)) / cos2
        x, y = player_x + cos * distance, player_y + sin * distance
        texture_x, texture_y = int(x * 3 % 1 * 99), int(y * 3 % 1 * 99)

        shading = 0.2 + 0.8 * (1 - row / HALF_VERTICAL_RESOLUTION)
        if maze[int(x - 0.33) % (MAP_SIZE - 1)][int(y - 0.33) % (MAP_SIZE - 1)] or \
           (maze[int(x - 0.33) % (MAP_SIZE - 1)][int(y) % (MAP_SIZE - 1)] and y % 1 > x % 1) or \
           (maze[int(x) % (MAP_SIZE - 1)][int(y - 0.33) % (MAP_SIZE - 1)] and x % 1 > y % 1):
            shading *= 0.5

        reflection = frame_buffer[column][2 * HALF_VERTICAL_RESOLUTION - row - 1]
        frame_buffer[column][2 * HALF_VERTICAL_RESOLUTION - row - 1] = (shading * (floor_texture[texture_x][texture_y] * 2 + reflection) / 4)

        # Check if the player is near the exit and apply a special effect
        if int(x) == exit_x and int(y) == exit_y and (x % 1 - 0.5) ** 2 + (y % 1 - 0.5) ** 2 < 0.2:
            exit_effect = row / (10 * HALF_VERTICAL_RESOLUTION)
            frame_buffer[column][row:2 * HALF_VERTICAL_RESOLUTION - row] = (exit_effect * np.ones(3) + frame_buffer[column][row:2 * HALF_VERTICAL_RESOLUTION - row]) / (1 + exit_effect)

    # Return the frame buffer
    return frame_buffer

@njit()
def new_frame(player_x, player_y, player_rotation, frame_buffer, sky_texture, floor_texture, maze, wall_texture, exit_x, exit_y):
    for column in range(HORIZONTAL_RESOLUTION):
        # Calculate the current rotation angle
        rotation_angle = player_rotation + np.deg2rad(column / SCALING_FACTOR - 30)
        sin = np.sin(rotation_angle)
        cos = np.cos(rotation_angle)
        cos2 = np.cos(np.deg2rad(column / SCALING_FACTOR - 30))
        frame_buffer[column][:] = sky_texture[int(np.rad2deg(rotation_angle) * 2 % 718)][:]

        x = player_x
        y = player_y

        # Render wall and floor
        frame_buffer, x, y, height = render_wall(x, y, maze, player_x, player_y, player_rotation, frame_buffer, wall_texture, column, cos, sin, cos2)
        frame_buffer = render_floor(x, y, height, cos2, player_x, cos, player_y, sin, frame_buffer, column, floor_texture, maze, exit_x, exit_y)
        
    return frame_buffer