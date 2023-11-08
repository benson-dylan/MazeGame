import pygame as pg
from OpenGL.GL import *
import numpy as np

class MazeGenerator:

    def __init__(self, mapSize):
        
        self.map_size = mapSize
        self.wall_boxes = []


    def generate_maze(self):
        # Generate a random maze layout with 1s (walls) and 0s (open paths)
        maze = np.random.choice([0, 0, 0, 0, 1, 1], (self.map_size, self.map_size))
        # Ensure the maze's border is surrounded by walls
        maze[0, :], maze[self.map_size-1, :], maze[:, 0], maze[:, self.map_size-1] = (1, 1, 1, 1)

        # Initialize the player's position and orientation
        player_x, player_y = 1.5, np.random.randint(1, self.map_size - 1) + .5
        x, y = int(player_x), int(player_y)
        
        # Mark the player's initial position as open
        maze[x][y] = 0
        count = 0

        # Find a valid location for the exit and pace it
        while True:
            # Create test coordinates based on current player (x, y) values
            test_x, test_y = (x, y)

            # Randomly decide to move in the x or y direction
            if np.random.uniform() > 0.5:
                test_x = test_x + np.random.choice([-1, 1])
            else:
                test_y = test_y + np.random.choice([-1, 1])

            # Check if the test coordinates are within the maze boundaries
            if test_x > 0 and test_x < self.map_size - 1 and test_y > 0 and test_y < self.map_size - 1:
                # Check if the test cell is open (0)
                if maze[test_x][test_y] == 0 or count > 5:
                    count = 0
                    x, y = (test_x, test_y)
                    maze[x][y] = 0

                    # Find a valid second-to-last column of the maze
                    if x == self.map_size - 2:
                        exit_x, exit_y = np.random.randint(1, self.map_size - 1), np.random.randint(1, self.map_size - 1)
                        break
                else:
                    count = count + 1

        self.create_wall_boxes(maze)

        return player_x, player_y, maze, exit_x, exit_y
    
    def create_wall_boxes(self, maze):
        wall_thickness = .9
        wall_height = 2.0 
        self.wall_boxes.clear()

        for y in range(self.map_size):
            for x in range(self.map_size):
                if maze[y][x] == 1:
                    position = np.array([x + 0.5, wall_height / 2, y + 0.5], dtype=np.float32)
                    size = np.array([1, wall_height, wall_thickness], dtype=np.float32)
                    self.wall_boxes.append({'position': position, 'size': size})
        for box in self.wall_boxes:
            print(f"Wall at position {box['position']} with size {box['size']}")