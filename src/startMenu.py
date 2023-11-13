import time
import time

import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
import numpy as np
import random
import pygame
import sys

from player import Player
from graphicsengine import GraphicsEngine, SimpleComponent, Object, Light

from sound import Sound
import pygame as pg

from mazeGenerator import MazeGenerator
from enemy import Enemy


class StartMenu:

    def __init__(self) -> None:
        # Simplified room dimensions
        self.cube_size = 5.0
        self.wall_height = 2.5

        self.floors = []
        self.ceilings = []
        self.walls = []

        self.renderRoom()

        # Player
        self.player = Player([0, 2, 0])

    def renderRoom(self):
    # Dimensions for walls, floor, and ceiling
        wall_thickness = 0.1  # Define the thickness of the walls
        room_size = self.cube_size * 5  # Define the size of the room

    # Create four walls
        for i in range(4):
            x = y = z = 0
            size = [0, 0, 0]

            if i == 0:  # Front wall
                x, y, z = room_size / 2, self.wall_height / 2, room_size / 2
                size = [wall_thickness, self.wall_height, room_size]
            elif i == 1:  # Back wall
                x, y, z = -room_size / 2, self.wall_height / 2, room_size / 2
                size = [wall_thickness, self.wall_height, room_size]
            elif i == 2:  # Left wall
                x, y, z = 0, self.wall_height / 2, room_size
                size = [room_size, self.wall_height, wall_thickness]
            elif i == 3:  # Right wall
                x, y, z = 0, self.wall_height / 2, 0
                size = [room_size, self.wall_height, wall_thickness]

            self.walls.append(
                SimpleComponent(position=[x, y, z], eulers=[0, 0, 0], size=size)
            )

    # Create floor
        self.floors.append(
            SimpleComponent(position=[0, 0, room_size / 2], eulers=[0, 0, 0], size=[room_size, wall_thickness, room_size])
        )

    # Create ceiling
        self.ceilings.append(
            SimpleComponent(position=[0, self.wall_height, room_size / 2], eulers=[0, 0, 0], size=[room_size, wall_thickness, room_size])
        )

    def update(self, rate):
        # Update method with removed collision detection and enemy logic
        pass

    def move_player(self, dPos):
        # Adjust this method to only allow camera movement (left and right)
        pass

    def move_player(self, dPos):
    # Assuming dPos contains the delta for the camera rotation
    # [delta_yaw, 0, 0] where delta_yaw is the change in camera rotation angle
        delta_yaw = dPos[0]
        self.spin_player(delta_yaw, 0)

    def spin_player(self, dTheta, dPhi):
        # Modify camera orientation horizontally
        self.player.theta += dTheta
        if self.player.theta > 360:
            self.player.theta -= 360
        elif self.player.theta < 0:
            self.player.theta += 360

        self.player.update_vectors()