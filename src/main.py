import pygame as pg
from OpenGL.GL import *
import numpy as np
import shaderLoaderV3 as sl
from utils import load_image
from input import escape_game, handle_camera_movement, handle_camera_target
from camera import Camera
from pyrr import *

pg.init()

pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 0)
pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

clock = pg.time.Clock()
pg.mouse.set_visible(False)

width = 800
height = 600
aspect = width / height

pg.display.set_mode((width, height), pg.OPENGL | pg.DOUBLEBUF)

glClearColor(0.2, 0.5, 0.2, 1.0)
glEnable(GL_DEPTH_TEST)

shader = sl.ShaderProgram("MazeGame/assets/shaders/vert.glsl", "MazeGame/assets/shaders/frag.glsl")

vertices = (
            # Position        # texture         # color
            -0.5, -0.5, 0.0,    0.0, 0.0,         1.0, 0.0, 0.0,      # vertex 1
             0.5, -0.5, 0.0,    1.0, 0.0,         0.0, 1.0, 0.0,      # vertex 2
             0.5,  0.5, 0.0,    1.0, 1.0,         0.0, 0.0, 1.0,       # vertex 3

            -0.5, -0.5, 0.0,    0.0, 0.0,         1.0, 0.0, 0.0,      # vertex 4
             0.5,  0.5, 0.0,    1.0, 1.0,         0.0, 0.0, 1.0,      # vertex 5
            -0.5,  0.5, 0.0,    0.0, 1.0,         0.0, 1.0, 0.0       # vertex 6
)
vertices = np.array(vertices, dtype=np.float32)

size_position = 3       # x, y, z
size_texture = 2        # s, t
size_color = 3          # r, g, b

stride = (size_position + size_texture + size_color) * 4   # size of a single vertex in bytes
offset_position = 0                                 # offset of the position data
offset_texture = size_position * 4                  # offset of the texture data. Texture data starts after 3 floats (12 bytes) of position data
offset_color = (size_position + size_texture) * 4   # offset of the color data. Color data starts after 5 floats (20 bytes) of position and texture data
n_vertices = len(vertices) // (size_position + size_texture + size_color)

vao = glGenVertexArrays(1)
glBindVertexArray(vao)                 # Bind the VAO. That is, make it the active one.

# Create a Vertex Buffer Object (VBO) to store the vertex data
vbo = glGenBuffers(1)                  # Generate one buffer and store its ID.
glBindBuffer(GL_ARRAY_BUFFER, vbo)     # Bind the buffer. That is, make it the active one.
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)   # Upload the data to the GPU.

position_loc = 0
glBindAttribLocation(shader.shader, position_loc, "position")
glVertexAttribPointer(position_loc, size_position, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset_position))
glEnableVertexAttribArray(position_loc)

# texture attribute
texture_loc = 1
glBindAttribLocation(shader.shader, texture_loc, "uv")
glVertexAttribPointer(texture_loc, size_texture, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset_texture))
glEnableVertexAttribArray(texture_loc)

color_loc = 2
glBindAttribLocation(shader.shader, color_loc, "color")
glVertexAttribPointer(color_loc, size_color, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset_color))
glEnableVertexAttribArray(color_loc)

img_data, img_width, img_height = load_image("../assets/textures/Front.bmp")

texture_id = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, texture_id)        # Bind the texture object. That is, make it the active one.
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)    # Set the texture wrapping parameters
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)    # Set texture filtering parameters
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img_width, img_height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
shader["tex"] = 0

glActiveTexture(GL_TEXTURE0)
glBindTexture(GL_TEXTURE_2D, texture_id)

camera = Camera([0.0, 0.0, 3.0], [0.0, 1.0, 0.0])
fov = 45
fov_radians = np.radians(fov)
projection_matrix = Matrix44.perspective_projection(fov_radians, aspect, 0.1, 1000)

draw = True
while draw:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            draw = False
        escape_game(event)

    pg.event.set_grab(True)

    keys = pg.key.get_pressed()
    mouse = pg.mouse.get_rel()
    handle_camera_movement(camera, keys)
    handle_camera_target(camera, mouse)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glUseProgram(shader.shader)  # Use the shader program

    camera.update_view_matrix()
    view_matrix = camera.get_view_matrix()
    glUniformMatrix4fv(glGetUniformLocation(shader.shader, "view"), 1, GL_FALSE, view_matrix)
    glUniformMatrix4fv(glGetUniformLocation(shader.shader, "projection"), 1, GL_FALSE, projection_matrix)

    # bind the VAO, and draw the triangle.
    glBindVertexArray(vao)
    glDrawArrays(GL_TRIANGLES, 0, n_vertices)      # Draw the triangle

    pg.display.flip()
    clock.tick(60)
    pg.event.pump()

pg.quit()
quit()



