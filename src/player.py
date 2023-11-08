import pygame as pg
from OpenGL.GL import *
import numpy as np
import pyrr

class Player:

    def __init__(self, position) -> None:
        
        self.position = np.array(position, dtype=np.float32)
        self.theta = 0
        self.phi = 0
        self.update_vectors()
        self.bounding_box_size = np.array([.5, .5, .5], dtype=np.float32)

    def update_vectors(self):

        self.forwards = np.array(
            [
                np.cos(np.deg2rad(self.theta)) * np.cos(np.deg2rad(self.phi)),
                np.sin(np.deg2rad(self.phi)),
                -np.sin(np.deg2rad(self.theta)) * np.cos(np.deg2rad(self.phi))
            ]
        )

        globalUp = np.array([0, 1, 0], dtype=np.float32)

        self.right = np.cross(self.forwards, globalUp)
        self.up = np.cross(self.right, self.forwards)

    def get_bounding_box(self):
        half_size = self.bounding_box_size / 2
        min_corner = self.position - half_size
        max_corner = self.position + half_size
        return min_corner, max_corner
    
    def get_bounding_box_at_position(self, position):
        half_size = self.bounding_box_size / 2
        min_corner = position - half_size
        max_corner = position + half_size
        return min_corner, max_corner