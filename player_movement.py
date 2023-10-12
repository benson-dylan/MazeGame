import pygame as pg
import numpy as np
from numba import njit

from constants import *

def movement(pressed_keys, player_x, player_y, player_rotation, map_height, elapsed_time):
    x, y, diag, diag = player_x, player_y, player_rotation, 0

    if pg.mouse.get_focused():
        mouse_movement = pg.mouse.get_rel()
        player_rotation = player_rotation + np.clip((mouse_movement[0]) / 200, -0.2, .2)

    if pressed_keys[pg.K_UP] or pressed_keys[ord('w')]:
        x, y, diag = x + elapsed_time * np.cos(player_rotation), y + elapsed_time * np.sin(player_rotation), 1

    elif pressed_keys[pg.K_DOWN] or pressed_keys[ord('s')]:
        x, y, diag = x - elapsed_time * np.cos(player_rotation), y - elapsed_time * np.sin(player_rotation), 1

    if pressed_keys[pg.K_LEFT] or pressed_keys[ord('a')]:
        elapsed_time = elapsed_time / (diag + 1)
        x, y = x + elapsed_time * np.sin(player_rotation), y - elapsed_time * np.cos(player_rotation)

    elif pressed_keys[pg.K_RIGHT] or pressed_keys[ord('d')]:
        elapsed_time = elapsed_time / (diag + 1)
        x, y = x - elapsed_time * np.sin(player_rotation), y + elapsed_time * np.cos(player_rotation)

    player_x, player_y = check_collision(player_x, player_y, map_height, x, y)

    return player_x, player_y, player_rotation


@njit(cache=True)
def check_collision(player_x, player_y, map_height, x, y):
    if not(map_height[int(x - 0.2)][int(y)] or map_height[int(x + 0.2)][int(y)] or
           map_height[int(x)][int(y - 0.2)] or map_height[int(x)][int(y + 0.2)]):
        player_x, player_y = x, y

    elif not(map_height[int(player_x - 0.2)][int(y)] or map_height[int(player_x + 0.2)][int(y)] or
             map_height[int(player_x)][int(y - 0.2)] or map_height[int(player_x)][int(y + 0.2)]):
        player_y = y

    elif not(map_height[int(x - 0.2)][int(player_y)] or map_height[int(x + 0.2)][int(player_y)] or
             map_height[int(x)][int(player_y - 0.2)] or map_height[int(x)][int(player_y + 0.2)]):
        player_x = x
        
    return player_x, player_y