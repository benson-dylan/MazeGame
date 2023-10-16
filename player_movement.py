import pygame as pg
import numpy as np
from numba import njit

from constants import *

def movement(pressed_keys, player_x, player_y, player_rotation, maze, elapsed_time):
    # Store the current player's position and rotation for reference
    x, y, diag, diag = player_x, player_y, player_rotation, 0

    if pg.mouse.get_focused():
        # Calculate the mouse movement and adjust the player's rotation accordingly
        mouse_movement = pg.mouse.get_rel()
        player_rotation = player_rotation + np.clip((mouse_movement[0]) / 200, -0.2, .2)

    if pressed_keys[pg.K_UP] or pressed_keys[ord('w')]:
        # Move the player forward
        x, y, diag = x + elapsed_time * np.cos(player_rotation), y + elapsed_time * np.sin(player_rotation), 1

    elif pressed_keys[pg.K_DOWN] or pressed_keys[ord('s')]:
        # Move the player backward
        x, y, diag = x - elapsed_time * np.cos(player_rotation), y - elapsed_time * np.sin(player_rotation), 1

    if pressed_keys[pg.K_LEFT] or pressed_keys[ord('a')]:
        # Move the player to the left
        elapsed_time = elapsed_time / (diag + 1)
        x, y = x + elapsed_time * np.sin(player_rotation), y - elapsed_time * np.cos(player_rotation)

    elif pressed_keys[pg.K_RIGHT] or pressed_keys[ord('d')]:
        # Move the player to the right
        elapsed_time = elapsed_time / (diag + 1)
        x, y = x - elapsed_time * np.sin(player_rotation), y + elapsed_time * np.cos(player_rotation)

    # Check for collisions in the updated player's position
    player_x, player_y = check_collision(player_x, player_y, maze, x, y)

    return player_x, player_y, player_rotation


@njit(cache=True)
def check_collision(player_x, player_y, maze, x, y):
    # Check if the desired position (x, y) is not blocked by maze walls
    if not(maze[int(x - 0.2)][int(y)] or maze[int(x + 0.2)][int(y)] or
           maze[int(x)][int(y - 0.2)] or maze[int(x)][int(y + 0.2)]):
        player_x, player_y = x, y   # If it's not blocked, update the player's position to (x, y)

    # Check if the player's current x position allows movement along the y-axis
    elif not(maze[int(player_x - 0.2)][int(y)] or maze[int(player_x + 0.2)][int(y)] or
             maze[int(player_x)][int(y - 0.2)] or maze[int(player_x)][int(y + 0.2)]):
        player_y = y    # If it's not blocked, update the player's y position to new y postion

    # Check if the player's current y position allows movement along the x-axis
    elif not(maze[int(x - 0.2)][int(player_y)] or maze[int(x + 0.2)][int(player_y)] or
             maze[int(x)][int(player_y - 0.2)] or maze[int(x)][int(player_y + 0.2)]):
        player_x = x    # If it's not blocked, update the player's x position to new x position
        
    return player_x, player_y