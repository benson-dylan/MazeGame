from OpenGL.GL import *
import numpy as np
import pyrr
import shaderLoaderV3 as sl
from utils import load_image
from objLoaderV4 import ObjLoader


class GraphicsEngine:

    def __init__(self):
        self.cube_mesh = CubeMesh()
        self.rayman = Mesh("../assets/models/raymanModel.obj")
        self.sky_texture = Material("../assets/textures/wood.png")
        self.shader = self.createShader("../assets/shaders/vertex.glsl", "../assets/shaders/fragment.glsl")

        glClearColor(0.2, 0.5, 0.5, 1)
        glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glUseProgram(self.shader.shader)
        glUniform1i(glGetUniformLocation(self.shader.shader, "imageTexture"), 0)

        projection_matrix = pyrr.matrix44.create_perspective_projection(45, 640/480, 0.1, 100, np.float32)
        glUniformMatrix4fv(glGetUniformLocation(self.shader.shader, "projection_matrix"), 1, GL_FALSE, projection_matrix)

        # self.modelMatrixLocation = glGetUniformLocation(self.shader.shader, "model_matrix")
        # self.viewMatrixLocation = glGetUniformLocation(self.shader.shader, "view_matrix")
        self.lightLocation = {
            "position": glGetUniformLocation(self.shader.shader, "Light.position"),
            "color": glGetUniformLocation(self.shader.shader, "Light.color"),
            "intensity": glGetUniformLocation(self.shader.shader, "Light.intensity")
        }

    def createShader(self, vertexFilepath, fragmentFilepath):
        shader = sl.ShaderProgram(vertexFilepath, fragmentFilepath)
        return shader 
    
    def render(self, scene):
        #Refresh screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUseProgram(self.shader.shader)
        

        view_transforms = pyrr.matrix44.create_look_at(scene.player.position, scene.player.position + scene.player.forwards, scene.player.up, dtype=np.float32)
        self.shader["view_matrix"] = view_transforms

        light = scene.lights[0]
        self.shader["light_pos"] = light.position
        glUniform3fv(self.lightLocation["color"], 1, light.color)
        glUniform1f(self.lightLocation["intensity"], light.intensity)

        self.sky_texture.use()
        glBindVertexArray(self.cube_mesh.vao)

        for cube in scene.cubes:
            model_transforms = pyrr.matrix44.create_identity(np.float32)
            model_transforms = pyrr.matrix44.multiply(model_transforms, pyrr.matrix44.create_from_eulers(np.radians(cube.eulers), dtype=np.float32))
            model_transforms = pyrr.matrix44.multiply(model_transforms, pyrr.matrix44.create_from_translation(cube.position, dtype=np.float32))
            self.shader["model_matrix"] = model_transforms
            glDrawArrays(GL_TRIANGLES, 0, self.cube_mesh.n_vertices)
        

        glBindVertexArray(self.rayman.vao)
        for object in scene.objects:
            model_transforms = pyrr.matrix44.create_identity(np.float32)
            model_transforms = pyrr.matrix44.multiply(model_transforms, pyrr.matrix44.create_from_eulers(np.radians(object.eulers), dtype=np.float32))
            model_transforms = pyrr.matrix44.multiply(model_transforms, pyrr.matrix44.create_from_translation(-self.rayman.center + object.position, dtype=np.float32))
            model_transforms = pyrr.matrix44.multiply(model_transforms, pyrr.matrix44.create_from_scale(np.array([1,1,1], dtype=np.float32) * self.rayman.scale, dtype=np.float32))
            self.shader["model_matrix"] = model_transforms
            glDrawArrays(GL_TRIANGLES, 0, self.rayman.n_vertices)
        
        
        glFlush()
    
    def quit(self):
        self.cube_mesh.destroy()
        self.rayman.destroy()
        glDeleteProgram(self.shader.shader)
        self.sky_texture.destroy()

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
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        img_data, img_width, img_height = load_image(filepath)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img_width, img_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)

    def destroy(self):
        glDeleteTextures(1, (self.texture,))

class Mesh:
    def __init__(self, fileName):
        self.obj = ObjLoader(fileName)
        self.vertices = self.obj.vertices
        self.n_vertices = self.obj.n_vertices
        self.dia = self.obj.dia
        self.scale = 4.0 / self.dia
        self.center = self.obj.center

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        #Position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        #Texture
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        #Normals
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(24))
    
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

class Object:
    def __init__(self, position, eulers):
        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)

class Light:

    def __init__(self, position, color, intensity):
        
        self.position = np.array(position, dtype=np.float32)
        self.color = np.array(color, dtype=np.float32)
        self.intensity = intensity