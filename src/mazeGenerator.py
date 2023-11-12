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
        maze[0, :], maze[self.map_size - 1, :], maze[:, 0], maze[:, self.map_size - 1] = (1, 1, 1, 1)

        # Initialize the player's position and orientation
        player_x, player_y = 1.5, np.random.randint(1, self.map_size - 1) + 0.5
        x, y = int(player_x), int(player_y)

        # Mark the player's initial position as open
        maze[x, y] = 0
        count = 0

        # Find a valid location for the exit and place it
        while True:
            # Create test coordinates based on the current player (x, y) values
            test_x, test_y = (x, y)

            # Randomly decide to move in the x or y direction
            if np.random.uniform() > 0.5:
                test_x = test_x + np.random.choice([-1, 1])
            else:
                test_y = test_y + np.random.choice([-1, 1])

            # Check if the test coordinates are within the maze boundaries
            if 0 < test_x < self.map_size - 1 and 0 < test_y < self.map_size - 1:
                # Check if the test cell is open (0)
                if maze[test_x, test_y] == 0 or count > 5:
                    count = 0
                    x, y = test_x, test_y
                    maze[x, y] = 0

                    # Check if the test cell is at the second-to-last column of the maze
                    if x == self.map_size - 2:
                        exit_x, exit_y = np.random.randint(1, self.map_size - 1, size=2)
                        # Check if the exit cell is open
                        if maze[exit_x, exit_y] == 0:
                            break
                else:
                    count += 1

        return player_x, player_y, maze, exit_x, exit_y
    
