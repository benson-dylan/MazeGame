import pygame as pg
from OpenGL.GL import *
import numpy as np
import shaderLoaderV3 as sl
import pyrr

from utils import load_image

class App:

    def __init__(self):
        
        # Pygame Setup
        pg.init()
        pg.display.set_mode((640, 480), pg.OPENGL | pg.DOUBLEBUF)
        self.clock = pg.time.Clock()
        #Background Color
        glClearColor(0.2, 0.5, 0.5, 1)
        glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.shader = self.createShader("../assets/shaders/vertex.glsl", "../assets/shaders/fragment.glsl")
        glUseProgram(self.shader.shader)
        glUniform1i(glGetUniformLocation(self.shader.shader, "imageTexture"), 0)
        self.cube = Cube(
            position=[0,0,-3],
            eulers=[0,0,0]
        )

        self.cube_mesh = CubeMesh()

        self.sky_texture = Material("../assets/textures/Teefy.png")

        projection_matrix = pyrr.matrix44.create_perspective_projection(45, 640/480, 0.1, 10, np.float32)
        glUniformMatrix4fv(glGetUniformLocation(self.shader.shader, "projection_matrix"), 1, GL_FALSE, projection_matrix)

        self.modelMatrixLocation = glGetUniformLocation(self.shader.shader, "model_matrix")

        self.mainLoop()

    def createShader(self, vertexFilepath, fragmentFilepath):
        shader = sl.ShaderProgram(vertexFilepath, fragmentFilepath)
        return shader 

    def mainLoop(self):
        
        draw = True
        while draw:
            #Check events
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    draw = False
            
            #Update Cube
            self.cube.eulers[2] += 0.2
            if(self.cube.eulers[2] > 360):
                self.cube.eulers[2] -= 360
            
            #Refresh screen
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            glUseProgram(self.shader.shader)
            self.sky_texture.use()

            model_transforms = pyrr.matrix44.create_identity(dtype=np.float32)
            model_transforms = pyrr.matrix44.multiply(model_transforms, pyrr.matrix44.create_from_eulers(np.radians(self.cube.eulers), dtype=np.float32))
            model_transforms = pyrr.matrix44.multiply(model_transforms, pyrr.matrix44.create_from_translation(self.cube.position, dtype=np.float32))

            glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, model_transforms)
            glBindVertexArray(self.cube_mesh.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.cube_mesh.n_vertices)
            pg.display.flip()

            #Timing
            self.clock.tick(60)
        self.quit()

    def quit(self):
        self.cube_mesh.destroy()
        glDeleteProgram(self.shader.shader)
        self.sky_texture.destroy()
        pg.QUIT

class Cube:

    def __init__(self, position, eulers):
        
        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)

class CubeMesh:

    def __init__(self):
        
        # x, y, z, s, t
        self.vertices = (
            -0.5, -0.5, -0.5, 0, 0,
             0.5, -0.5, -0.5, 1, 0,
             0.5,  0.5, -0.5, 1, 1,

             0.5,  0.5, -0.5, 1, 1,
            -0.5,  0.5, -0.5, 0, 1,
            -0.5, -0.5, -0.5, 0, 0,

            -0.5, -0.5,  0.5, 0, 0,
             0.5, -0.5,  0.5, 1, 0,
             0.5,  0.5,  0.5, 1, 1,

             0.5,  0.5,  0.5, 1, 1,
            -0.5,  0.5,  0.5, 0, 1,
            -0.5, -0.5,  0.5, 0, 0,

            -0.5,  0.5,  0.5, 1, 0,
            -0.5,  0.5, -0.5, 1, 1,
            -0.5, -0.5, -0.5, 0, 1,

            -0.5, -0.5, -0.5, 0, 1,
            -0.5, -0.5,  0.5, 0, 0,
            -0.5,  0.5,  0.5, 1, 0,

             0.5,  0.5,  0.5, 1, 0,
             0.5,  0.5, -0.5, 1, 1,
             0.5, -0.5, -0.5, 0, 1,

             0.5, -0.5, -0.5, 0, 1,
             0.5, -0.5,  0.5, 0, 0,
             0.5,  0.5,  0.5, 1, 0,

            -0.5, -0.5, -0.5, 0, 1,
             0.5, -0.5, -0.5, 1, 1,
             0.5, -0.5,  0.5, 1, 0,

             0.5, -0.5,  0.5, 1, 0,
            -0.5, -0.5,  0.5, 0, 0,
            -0.5, -0.5, -0.5, 0, 1,

            -0.5,  0.5, -0.5, 0, 1,
             0.5,  0.5, -0.5, 1, 1,
             0.5,  0.5,  0.5, 1, 0,

             0.5,  0.5,  0.5, 1, 0,
            -0.5,  0.5,  0.5, 0, 0,
            -0.5,  0.5, -0.5, 0, 1
        )

        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.n_vertices = len(self.vertices) // 5

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12))
        

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

class Material:

    def __init__(self, filepath):
        
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        img_data, img_width, img_height = load_image(filepath)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img_width, img_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)

    def destroy(self):
        glDeleteTextures(1, (self.texture,))

if __name__ == "__main__":
    myApp = App()




