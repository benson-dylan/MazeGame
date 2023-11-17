import random
from mazelib import Maze
from mazelib.generate.Prims import Prims

class MazeGenerator:
    def __init__(self):
        self.maze = None
        self.exit_x = None
        self.exit_y = None

    def generate_maze(self, maze_size):
        # Generate the maze
        m = Maze()
        m.generator = Prims(maze_size, maze_size)
        m.generate()

        # Convert the maze to a 2D array
        maze_2d_array = [[1 if cell == '#' else 0 for cell in row] for row in str(m).split('\n') if row.strip()]

        # Find open cells in the maze
        open_cells = [(i, j) for i, row in enumerate(maze_2d_array) for j, cell in enumerate(row) if cell == 0]


        # Set the maze attribute
        self.maze = maze_2d_array

        # Return the results
        return self.maze