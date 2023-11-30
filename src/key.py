import pygame as pg
from OpenGL.GL import *
import numpy as np
import math

class Key:
    def __init__(self, position, size=(1, 1, 1)):
        self.position = np.array(position, dtype=np.float32)
        self.original_y_position = self.position[1]  
        self.size = np.array(size, dtype=np.float32)  
        self.collected = False
        self.bobbing_phase = 0.0  
        self.rotation = 0.0  

        self.calculate_bounding_box()

    def calculate_bounding_box(self):
        half_size = self.size / 2
        self.min_corner = self.position - half_size
        self.max_corner = self.position + half_size
        self.bounding_box = (self.min_corner, self.max_corner)

    def collect(self):
        self.collected = True

    def get_bounding_box(self):
        return self.min_corner, self.max_corner

    def update(self, rate, camera_direction):
        if self.collected:
            return

        self.bobbing_phase += rate
        bobbing_height = 0.2 * math.sin(self.bobbing_phase) 
        self.position[1] = self.original_y_position + bobbing_height
        self.rotation = np.arctan2(camera_direction[0], camera_direction[2])
