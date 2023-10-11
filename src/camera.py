import numpy as np
from math import radians, sin, cos
from pyrr import *

class Camera:
    def __init__(self, initial_position, initial_up):
        self.position = np.array(initial_position, dtype=np.float32)
        self.target = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        self.up = np.array(initial_up, dtype=np.float32)
        self.speed = 0.2
        self.sensitivity = 0.01
    
    def update_view_matrix(self):
        self.view_matrix = Matrix44.look_at(self.position, self.target, self.up)
        
    def get_view_matrix(self):
        return self.view_matrix
    
    def move(self, direction):
        self.position += direction * self.speed
    
    def move_forward(self):
        self.position += self.target * self.speed

    def move_backward(self):
        self.position -= self.target * self.speed

    def move_left(self):
        self.position -= np.array([1.0, 0.0, 0.0], dtype=np.float32) * self.speed

    def move_right(self):
        self.position += np.array([1.0, 0.0, 0.0], dtype=np.float32) * self.speed
    
    def update_target(self, delta_x, delta_y):
        delta_x *= self.sensitivity
        delta_y *= self.sensitivity

        self.target[0] += delta_x
        self.target[1] = np.clip(self.target[1] - delta_y, -90, 90)

