import pygame as pg
import numpy as np
from numba import njit

from constants import *

def load_sprites():
    zombie_skeleton_sheet  = pg.image.load('zombie_n_skeleton4.png').convert_alpha()
    sprites = [[], []]

    for i in range(3):
        xx = i*32
        sprites[0].append([])
        sprites[1].append([])
        for j in range(4):
            yy = j * 100
            sprites[0][i].append(pg.Surface.subsurface(zombie_skeleton_sheet ,(xx , yy, 32, 100)))
            sprites[1][i].append(pg.Surface.subsurface(zombie_skeleton_sheet ,(xx + 96, yy, 32, 100)))

    sprite_size = np.asarray(sprites[0][1][0].get_size()) * HORIZONTAL_RESOLUTION / 800

    
    return sprites, sprite_size

def draw_sprites(surface, sprites, enemies, sprite_size, ticks):
    # Animation cycle for monsters
    cycle = int(ticks) % 3
    for en in range(len(enemies)):
        if enemies[en][3] >  10:
            break
        
        types = int(enemies[en][4])
        direction_to_player = int(enemies[en][7])
        cos2 = np.cos(enemies[en][2])
        scale = min(enemies[en][3], 2) * sprite_size * enemies[en][5] / cos2
        vert = HALF_VERTICAL_RESOLUTION + HALF_VERTICAL_RESOLUTION * min(enemies[en][3], 2) / cos2
        hor = HORIZONTAL_RESOLUTION / 2 - HORIZONTAL_RESOLUTION * np.sin(enemies[en][2])
        sp_surf = pg.transform.scale(sprites[types][cycle][direction_to_player], scale)
        surface.blit(sp_surf, (hor, vert) - scale / 2)

    return surface, en-1