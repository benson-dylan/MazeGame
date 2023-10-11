from OpenGL.GL import *
from pyrr import *
import numpy as np

front_vertices = (
            # Position        # texture         # color
            -5.0, -5.0, 0.0,    0.0, 0.0,         1.0, 0.0, 0.0,      # vertex 1
             5.0, -5.0, 0.0,    1.0, 0.0,         0.0, 1.0, 0.0,      # vertex 2
             5.0,  5.0, 0.0,    1.0, 1.0,         0.0, 0.0, 1.0,       # vertex 3

            -5.0, -5.0, 0.0,    0.0, 0.0,         1.0, 0.0, 0.0,      # vertex 4
             5.0,  5.0, 0.0,    1.0, 1.0,         0.0, 0.0, 1.0,      # vertex 5
            -5.0,  5.0, 0.0,    0.0, 1.0,         0.0, 1.0, 0.0       # vertex 6
)

front_vertices = np.array(front_vertices, dtype=np.float32)

size_position = 3       # x, y, z
size_texture = 2        # s, t
size_color = 3          # r, g, b

stride = (size_position + size_texture + size_color) * 4   # size of a single vertex in bytes
offset_position = 0                                 # offset of the position data
offset_texture = size_position * 4                  # offset of the texture data. Texture data starts after 3 floats (12 bytes) of position data
offset_color = (size_position + size_texture) * 4   # offset of the color data. Color data starts after 5 floats (20 bytes) of position and texture data
n_vertices = len(front_vertices) // (size_position + size_texture + size_color)