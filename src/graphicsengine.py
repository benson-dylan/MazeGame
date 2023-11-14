import time
from OpenGL.GL import *
import numpy as np
import pyrr
import shaderLoaderV3 as sl
from utils import load_image
from objLoaderV4 import ObjLoader
import math



class GraphicsEngine:

    def __init__(self, numLights):
        # self.cube_mesh = CubeWallMesh()
        self.rayman = Mesh("assets/models/raymanModel.obj")
        self.square = Mesh("assets/models/square.obj")
        self.floor = Floor(w=5.0, h=5.0)

        self.wall_mesh = CubeWallMesh() 

        self.ceiling = Ceiling(w=5.0, h=5.0)
        self.wood_texture = Material("assets/textures/wood.png")
        self.rayman_texture = Material("assets/textures/raymanModel.png", "rayman")
        self.shader = self.createShader("assets/shaders/vertex.glsl", "assets/shaders/fragment.glsl")
        self.light_shader = self.createShader("assets/shaders/vertex_light.glsl", "assets/shaders/fragment_light.glsl")

        # Changed the texture to a compressed version, might help with performance
        self.carpet_texture = Material("assets/textures/compressed/dirtycarpet-min.png")
        self.wall_texture = Material("assets/textures/compressed/yellowwallpaper-min.jpg")
        self.ceiling_texture = Material("assets/textures/compressed/ceiling-tile-min.png")

        # Enemy 
        self.enemy_texture_1 = Material("assets/textures/enemy/45.png")
        self.enemy_texture_2 = Material("assets/textures/enemy/46.png")
        self.enemy_texture_3 = Material("assets/textures/enemy/47.png")
        self.enemy_texture_4 = Material("assets/textures/enemy/48.png")
        self.enemy_billboard = BillBoard(w=0.5, h=0.5)

        self.teefy_texture = Material("assets/textures/teefy.png")
        self.teefy_billboard = BillBoard(w=0.5, h=0.5)
        
        self.light_texture = Material("assets/textures/lightbulb.png")
        self.light_billboard = BillBoard(w=0.2, h=0.2)
        self.num_light_loc = glGetUniformLocation(self.shader.shader, "numLights")

        #Key
        self.key_texture = Material("assets/textures/key.png")
        self.key_billboard = BillBoard(w=0.2, h=0.2)

        glClearColor(0.2, 0.5, 0.5, 1)
        glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        #glEnable(GL_CULL_FACE)
        #glCullFace(GL_BACK)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glUseProgram(self.shader.shader)
        glUniform1i(glGetUniformLocation(self.shader.shader, "imageTexture"), 0)
        glUniform1i(self.num_light_loc, numLights)

        projection_matrix = pyrr.matrix44.create_perspective_projection(45, 640/480, 0.1, 100, np.float32)
        glUniformMatrix4fv(glGetUniformLocation(self.shader.shader, "projection_matrix"), 1, GL_FALSE, projection_matrix)

        self.lightLocation = {
            "position":[
                glGetUniformLocation(self.shader.shader, f"Lights[{i}].position")
                for i in range(numLights)
            ],
            "color": [
                glGetUniformLocation(self.shader.shader, f"Lights[{i}].color")
                for i in range(numLights)
            ],
            "intensity": [
                glGetUniformLocation(self.shader.shader, f"Lights[{i}].intensity")
                for i in range(numLights)
            ],
        }
        self.cameraPosLoc = glGetUniformLocation(self.shader.shader, "cameraPosition")

        glUseProgram(self.light_shader.shader)
        glUniformMatrix4fv(glGetUniformLocation(self.light_shader.shader, "projection_matrix"), 1, GL_FALSE, projection_matrix)
        self.tintLoc = glGetUniformLocation(self.light_shader.shader, "tint")

    def createShader(self, vertexFilepath, fragmentFilepath):
        shader = sl.ShaderProgram(vertexFilepath, fragmentFilepath)
        return shader 
    
    def render(self, scene):
        #Refresh screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUseProgram(self.shader.shader)
    
        view_transforms = pyrr.matrix44.create_look_at(scene.player.position, scene.player.position + scene.player.forwards, scene.player.up, dtype=np.float32)
        self.shader["view_matrix"] = view_transforms
    
        for i, light in enumerate(scene.lights):
            glUniform3fv(self.lightLocation["position"][i], 1, light.position)
            glUniform3fv(self.lightLocation["color"][i], 1, light.color)
            glUniform1f(self.lightLocation["intensity"][i], light.intensity)

        glUniform3fv(self.cameraPosLoc, 1, scene.player.position)

        
        for wall in scene.walls:

            self.wall_texture.use()

            model_transforms = pyrr.matrix44.create_identity(np.float32)
            model_transforms = pyrr.matrix44.multiply(model_transforms, pyrr.matrix44.create_from_eulers(np.radians(wall.eulers), dtype=np.float32))
            model_transforms = pyrr.matrix44.multiply(model_transforms, pyrr.matrix44.create_from_translation(wall.position, dtype=np.float32))
            self.shader["model_matrix"] = model_transforms
            glBindVertexArray(self.wall_mesh.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.wall_mesh.n_vertices)
        

        # self.rayman_texture.use()
        # for object in scene.objects:
        #     model_transforms = pyrr.matrix44.create_identity(np.float32)
        #     model_transforms = pyrr.matrix44.multiply(model_transforms, pyrr.matrix44.create_from_eulers(np.radians(object.eulers), dtype=np.float32))
        #     model_transforms = pyrr.matrix44.multiply(model_transforms, pyrr.matrix44.create_from_translation(-self.rayman.center + object.position, dtype=np.float32))
        #     model_transforms = pyrr.matrix44.multiply(model_transforms, pyrr.matrix44.create_from_scale(np.array([1,1,1], dtype=np.float32) * self.rayman.scale, dtype=np.float32))
        #     self.shader["model_matrix"] = model_transforms
        #     glBindVertexArray(self.rayman.vao)
        #     glDrawArrays(GL_TRIANGLES, 0, self.rayman.n_vertices)

        self.carpet_texture.use()
        for floor in scene.floors:
            model_transforms = pyrr.matrix44.create_identity(np.float32)
            model_transforms = pyrr.matrix44.multiply(model_transforms, pyrr.matrix44.create_from_z_rotation(np.deg2rad(90), dtype=np.float32))
            model_transforms = pyrr.matrix44.multiply(model_transforms, pyrr.matrix44.create_from_translation(floor.position, dtype=np.float32))
            model_transforms = pyrr.matrix44.multiply(model_transforms, pyrr.matrix44.create_from_scale(np.array([1,1,1], dtype=np.float32), dtype=np.float32))
            self.shader["model_matrix"] = model_transforms
            glBindVertexArray(self.floor.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.square.n_vertices)

        self.ceiling_texture.use()
        for ceiling in scene.ceilings:
            model_transforms = pyrr.matrix44.create_identity(np.float32)
            model_transforms = pyrr.matrix44.multiply(model_transforms, pyrr.matrix44.create_from_z_rotation(np.deg2rad(270), dtype=np.float32))
            model_transforms = pyrr.matrix44.multiply(model_transforms, pyrr.matrix44.create_from_translation(ceiling.position, dtype=np.float32))
            model_transforms = pyrr.matrix44.multiply(model_transforms, pyrr.matrix44.create_from_scale(np.array([1,1,1], dtype=np.float32), dtype=np.float32))
            self.shader["model_matrix"] = model_transforms
            glBindVertexArray(self.ceiling.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.square.n_vertices)

        # for teefy in scene.teefys:

        #     self.teefy_texture.use()

        #     directionFromPlayer = teefy.position - scene.player.position
        #     angle1 = np.arctan2(directionFromPlayer[0], -directionFromPlayer[2]) # X, Z
        #     dist2d = math.sqrt(directionFromPlayer[0]**2 + directionFromPlayer[2]**2)
        #     angle2 = np.arctan2(directionFromPlayer[1], dist2d)

        #     model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
        #     model_transform = pyrr.matrix44.multiply(model_transform, pyrr.matrix44.create_from_z_rotation(theta=angle2, dtype=np.float32))
        #     model_transform = pyrr.matrix44.multiply(model_transform, pyrr.matrix44.create_from_y_rotation(theta=angle1 + math.pi / 2, dtype=np.float32))
        #     model_transform = pyrr.matrix44.multiply(model_transform, pyrr.matrix44.create_from_translation(teefy.position, dtype=np.float32))

        #     self.shader["model_matrix"] = model_transform
        #     glBindVertexArray(self.teefy_billboard.vao)
        #     glDrawArrays(GL_TRIANGLES, 0, self.teefy_billboard.n_vertices)

        ''' Enemy '''
        # Loop through the animation
        current_texture_index = int((time.time() % 1) // 0.25) + 1  # Change textures every 0.25 seconds
        current_texture_index = (current_texture_index - 1) % 4 + 1  # Ensure it stays within the range [1, 4]
        current_texture = getattr(self, f"enemy_texture_{current_texture_index}")
        current_texture.use()
        for enemy in scene.enemies:
            teefy_position = np.array(enemy.position)
            player_position = np.array(scene.player.position)

            direction_from_player = teefy_position - player_position
            angle1 = np.arctan2(direction_from_player[0], -direction_from_player[2])  # X, Z
            dist2d = np.sqrt(direction_from_player[0]**2 + direction_from_player[2]**2)
            angle2 = np.arctan2(direction_from_player[1], dist2d)

            model_transform = pyrr.matrix44.create_identity(dtype=np.float32)

            # Adjust the scaling factor to increase the size of the texture
            scaling_factor = enemy.size  # You can adjust this value as needed
            model_transform = pyrr.matrix44.multiply(model_transform, pyrr.matrix44.create_from_scale(np.array([scaling_factor, scaling_factor, scaling_factor], dtype=np.float32), dtype=np.float32))

            model_transform = pyrr.matrix44.multiply(model_transform, pyrr.matrix44.create_from_z_rotation(theta=angle2, dtype=np.float32))
            model_transform = pyrr.matrix44.multiply(model_transform, pyrr.matrix44.create_from_y_rotation(theta=angle1 + math.pi / 2, dtype=np.float32))
            model_transform = pyrr.matrix44.multiply(model_transform, pyrr.matrix44.create_from_translation(teefy_position, dtype=np.float32))

            self.shader["model_matrix"] = model_transform
            glBindVertexArray(self.enemy_billboard.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.enemy_billboard.n_vertices)

        # ----------------------------------------------------


        # Render keys
        self.key_texture.use()
        for key in scene.keys:
            if key.collected:
                continue

            key_position = np.array(key.position)
            key_rotation = key.rotation
            model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
            scaling_factor = 5.0  
            model_transform = pyrr.matrix44.multiply(model_transform, pyrr.matrix44.create_from_scale(np.array([scaling_factor, scaling_factor, scaling_factor], dtype=np.float32)))
            model_transform = pyrr.matrix44.multiply(model_transform, pyrr.matrix44.create_from_y_rotation(theta=key_rotation))
            model_transform = pyrr.matrix44.multiply(model_transform, pyrr.matrix44.create_from_translation(key_position, dtype=np.float32))
            self.shader["model_matrix"] = model_transform
            glBindVertexArray(self.key_billboard.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.key_billboard.n_vertices)


        self.shader["model_matrix"] = model_transform
        glBindVertexArray(self.teefy_billboard.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.teefy_billboard.n_vertices)

        glUseProgram(self.light_shader.shader)

        self.light_shader["view_matrix"] = view_transforms

        # for light in scene.lights:
            
        #     self.light_texture.use()
        #     glUniform3fv(self.tintLoc, 1, light.color)

        #     directionFromPlayer = light.position - scene.player.position
        #     angle1 = np.arctan2(directionFromPlayer[0], -directionFromPlayer[2]) # X, Z
        #     dist2d = math.sqrt(directionFromPlayer[0]**2 + directionFromPlayer[2]**2)
        #     angle2 = np.arctan2(directionFromPlayer[1], dist2d)

        #     model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
        #     model_transform = pyrr.matrix44.multiply(model_transform, pyrr.matrix44.create_from_z_rotation(theta=angle2, dtype=np.float32))
        #     model_transform = pyrr.matrix44.multiply(model_transform, pyrr.matrix44.create_from_y_rotation(theta=angle1 + math.pi / 2, dtype=np.float32))
        #     model_transform = pyrr.matrix44.multiply(model_transform, pyrr.matrix44.create_from_translation(light.position, dtype=np.float32))

        #     self.light_shader["model_matrix"] = model_transform
        #     glBindVertexArray(self.light_billboard.vao)
        #     glDrawArrays(GL_TRIANGLES, 0, self.light_billboard.n_vertices)

        glUniform3fv(self.tintLoc, 1, np.array([1, 1, 1], dtype=np.float32))

        glFlush()


    
    def quit(self):
        self.wall_mesh.destroy()
        self.rayman.destroy()
        self.square.destroy
        self.teefy_billboard.destroy()
        self.teefy_texture.destroy()
        self.light_billboard.destroy()
        self.light_texture.destroy()
        self.wood_texture.destroy()
        glDeleteProgram(self.shader.shader)
       

class SimpleComponent:

    def __init__(self, position, eulers, size):
        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)
        self.size = np.array(size, dtype=np.float32)

    def calculate_bounding_box(self):
        half_size = self.size / 2
        self.min_corner = self.position - half_size
        self.max_corner = self.position + half_size
        self.bounding_box = (self.min_corner, self.max_corner)
        return self.bounding_box

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
        
# CUBE WALL
class CubeWallMesh:
    def __init__(self):
        # x, y, z, s, t, n
        self.vertices = (
            #Front Face
            -2.5, -2.5, -2.5, 0, 0, 0, 0, -1,
             2.5, -2.5, -2.5, 1, 0, 0, 0, -1,
             2.5,  2.5, -2.5, 1, 1, 0, 0, -1,

             2.5,  2.5, -2.5, 1, 1, 0, 0, -1,
            -2.5,  2.5, -2.5, 0, 1, 0, 0, -1,
            -2.5, -2.5, -2.5, 0, 0, 0, 0, -1,

            #Back Face
            -2.5, -2.5,  2.5, 0, 0, 0, 0,  1,
             2.5, -2.5,  2.5, 1, 0, 0, 0,  1,
             2.5,  2.5,  2.5, 1, 1, 0, 0,  1,

             2.5,  2.5,  2.5, 1, 1, 0, 0,  1,
            -2.5,  2.5,  2.5, 0, 1, 0, 0,  1,
            -2.5, -2.5,  2.5, 0, 0, 0, 0,  1,

            #Left Face
            -2.5,  2.5,  2.5, 1, 0, -1, 0, 0,
            -2.5,  2.5, -2.5, 1, 1, -1, 0, 0,
            -2.5, -2.5, -2.5, 0, 1, -1, 0, 0,

            -2.5, -2.5, -2.5, 0, 1, -1, 0, 0,
            -2.5, -2.5,  2.5, 0, 0, -1, 0, 0,
            -2.5,  2.5,  2.5, 1, 0, -1, 0, 0,
            #Right Face
             2.5,  2.5,  2.5, 1, 0, 1, 0, 0,
             2.5,  2.5, -2.5, 1, 1, 1, 0, 0,
             2.5, -2.5, -2.5, 0, 1, 1, 0, 0,

             2.5, -2.5, -2.5, 0, 1, 1, 0, 0,
             2.5, -2.5,  2.5, 0, 0, 1, 0, 0,
             2.5,  2.5,  2.5, 1, 0, 1, 0, 0,
        )

        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.n_vertices = len(self.vertices) // 5

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))
        

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

class Material:

    def __init__(self, filepath, model=""):
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
        img_data, img_width, img_height = load_image(filepath, "RGBA", False)

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
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))
    
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

class BillBoard:

    def __init__(self, w, h):
        #x, y, z, s, t, n
        self.vertices = (
            0, h/2, -w/2, 0, 0, -1, 0, 0,
            0, -h/2, -w/2, 0, 1, -1, 0, 0,
            0, -h/2, w/2, 1, 1, -1, 0, 0,

            0, h/2, -w/2, 0, 0, -1, 0, 0,
            0, -h/2, w/2, 1, 1, -1, 0, 0,
            0, h/2, w/2, 1, 0, -1, 0, 0,
        )

        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.n_vertices = len(self.vertices) // 8

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
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

class Floor:

    def __init__(self, w, h):
        #x, y, z, s, t, n
        self.vertices = (
            0, h/2, -w/2, 0, 0, -1, 0, 0,
            0, -h/2, -w/2, 0, 1, -1, 0, 0,
            0, -h/2, w/2, 1, 1, -1, 0, 0,

            0, h/2, -w/2, 0, 0, -1, 0, 0,
            0, -h/2, w/2, 1, 1, -1, 0, 0,
            0, h/2, w/2, 1, 0, -1, 0, 0,
        )

        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.n_vertices = len(self.vertices) // 8

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
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

class Wall:

    def __init__(self, w, h):
        #x, y, z, s, t, n
        self.vertices = (
            0, h/2, -w/2, 0, 0, -1, 0, 0,
            0, -h/2, -w/2, 0, 1, -1, 0, 0,
            0, -h/2, w/2, 1, 1, -1, 0, 0,
            
            0, h/2, -w/2, 0, 0, -1, 0, 0,
            0, -h/2, w/2, 1, 1, -1, 0, 0,
            0, h/2, w/2, 1, 0, -1, 0, 0,
        )

        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.n_vertices = len(self.vertices) // 8

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
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))

    def calculate_bounding_box(self):
        half_size = self.size / 2
        min_corner = self.position - half_size
        max_corner = self.position + half_size
        return min_corner, max_corner

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

class Ceiling:

    def __init__(self, w, h):
        #x, y, z, s, t, n
        self.vertices = (
            0, h/2, -w/2, 0, 0, -1, 0, 0,
            0, -h/2, -w/2, 0, 1, -1, 0, 0,
            0, -h/2, w/2, 1, 1, -1, 0, 0,

            0, h/2, -w/2, 0, 0, -1, 0, 0,
            0, -h/2, w/2, 1, 1, -1, 0, 0,
            0, h/2, w/2, 1, 0, -1, 0, 0,
        )

        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.n_vertices = len(self.vertices) // 8

        self.max = np.max(self.vertices, axis=0)
        self.min = np.min(self.vertices, axis=0)
        self.center = (self.max + self.min) / 2

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
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))
