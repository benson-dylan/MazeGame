import time
import time
import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
import numpy as np

from player import Player
from graphicsengine import GraphicsEngine, SimpleComponent, Object, Light

from sound import Sound
import pygame as pg

from mazeGenerator import MazeGenerator

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
RETURN_ACTION_CONTINUE = 0
RETURN_ACTION_END = 1

def initialize_glfw():

    glfw.init()
    glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_PROFILE, GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE)
    glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, GLFW_CONSTANTS.GLFW_TRUE)
    glfw.window_hint(GLFW_CONSTANTS.GLFW_DOUBLEBUFFER, GL_FALSE)

    window = glfw.create_window(SCREEN_WIDTH, SCREEN_HEIGHT, "My Game", None, None)

    glfw.make_context_current(window)
    glfw.set_input_mode(window, GLFW_CONSTANTS.GLFW_CURSOR, GLFW_CONSTANTS.GLFW_CURSOR_HIDDEN)

    return window

class Scene:

    def __init__(self) -> None:
        self.maze_size = 10
        self.walls = []
        cube_size = 5.0
        wall_height = 2.5

        self.mazeGenerator = MazeGenerator(self.maze_size)
        self.player_x, self.player_y, self.maze, self.exit_x, self.exit_y = self.mazeGenerator.generate_maze()
        print(self.maze)
        print("Player Location", self.player_x, self.player_y)
        print("Exit Location", self.exit_x, self.exit_y)

        self.teefys = [
            SimpleComponent(
                position= [2,2,0],
                eulers= [0,0,0],
                size=0
            ),
            SimpleComponent(
                position= [5,2,2],
                eulers= [0,0,0],
                size=0
            ),
        ]

        '''
        Generate the walls
        '''
        for i in range(len(self.maze)):
            for j in range(len(self.maze[i])):
                if self.maze[i][j] == 1:
                    x = j * cube_size
                    y = wall_height / 2
                    z = i * cube_size
                    wall_size = [cube_size, wall_height, cube_size]
                    wall_component = SimpleComponent(
                        position=[x, y, z],
                        eulers=[0, 0, 0],
                        size=wall_size
            )
                    wall_component.calculate_bounding_box()
                    self.walls.append(wall_component)
        '''
        Generate the floors
        '''
        # Define the dimensions of the maze
        maze_height = len(self.maze)
        maze_width = len(self.maze[0])

        # Generate floors for the maze
        self.floors = []

        for row in range(maze_height):
            for col in range(maze_width):
                # Multiply the x and y positions by 5 to create the floor
                x_position = col * 5
                z_position = row * 5

                self.floors.append(
                    SimpleComponent(
                        position=[x_position, 0, z_position],
                        eulers= [0, 0, 0],
                        size=0
                    )
                )
                    
       
        '''
        Generate the ceilings
        '''
        self.ceilings = []
        for row in range(maze_height):
            for col in range(maze_width):
                # Multiply the x and y positions by 5 to create the floor
                x_position = col * 5
                z_position = row * 5

                self.ceilings.append(
                    SimpleComponent(
                        position=[x_position, 5, z_position],
                        eulers= [0, 0, 0],
                        size=0
                    )
                )

        
        self.objects = []
        self.player = Player([self.player_y * 5, 2 , self.player_x * 5])
        
        self.lights = [
        
        ]

        # Play the ambient sound
        self.sound = Sound()
        pg.mixer.music.play(-1)

        self.play = self.sound.play
        # Initialize footstep time
        self.last_footstep_time = 0
        self.footstep_delay = 0.5

        if self.check_immediate_collisions():
            print("Collision detected at the start position!")

    def update(self, rate):
        
        for object in self.objects:
            object.eulers[2] += 0.25 * rate
            if object.eulers[2] > 360:
                object.eulers[2] -= 360

        # OBJECT COLLISION #
        """ for teefy in self.teefys:
            vector = self.player.position - teefy.position
            distance = np.sqrt(vector[0] ** 2 + vector[2] ** 2)
            print(distance)
            if distance < 1:
                teefy.position[1] += 100 """
        
    def check_immediate_collisions(self):
        player_min_corner, player_max_corner = self.player.get_bounding_box()
        for wall_box in self.mazeGenerator.wall_boxes:
            wall_min_corner = wall_box['position'] - wall_box['size'] / 2
            wall_max_corner = wall_box['position'] + wall_box['size'] / 2
            if self.check_collision(player_min_corner, player_max_corner, wall_min_corner, wall_max_corner):
                print(f"Immediate collision at start with wall at: {wall_box['position']}")
                return True
        return False
    
    def check_collision(self, player_min, player_max, wall_min, wall_max):
        overlap_x = (wall_min[0] < player_max[0]) and (player_min[0] < wall_max[0])
        overlap_y = (wall_min[1] < player_max[1]) and (player_min[1] < wall_max[1])
        overlap_z = (wall_min[2] < player_max[2]) and (player_min[2] < wall_max[2])
        return overlap_x and overlap_y and overlap_z

    
    def move_player(self, dPos):
        dPos = np.array(dPos, dtype=np.float32)
        for axis in range(3):
            new_position = self.player.position.copy()
            new_position[axis] += dPos[axis]
            player_min_corner, player_max_corner = self.player.get_bounding_box_at_position(new_position)
            collision = False
            for wall in self.walls: 
                if self.check_collision(player_min_corner, player_max_corner, wall.min_corner, wall.max_corner):
                    print("collision detected")
                    collision = True
                    dPos[axis] = 0
                    break
            if not collision:
                self.player.position[axis] += dPos[axis]
        if np.any(dPos):
            self.update_footsteps()

    def update_footsteps(self):
        current_time = time.time()
        if current_time - self.last_footstep_time >= self.footstep_delay:
            self.play(self.sound.player_move)
            self.last_footstep_time = current_time



    def spin_player(self, dTheta, dPhi):

        self.player.theta += dTheta
        if self.player.theta > 360:
            self.player.theta -= 360
        elif self.player.theta < 0:
            self.player.theta += 360

        self.player.phi = min(89, max(-89, self.player.phi + dPhi))

        self.player.update_vectors()

class App:

    def __init__(self, window):
        
        self.window = window
        self.renderer = GraphicsEngine()
        self.scene = Scene()

        self.lastTime = glfw.get_time()
        self.currentTime = 0
        self.numFrames = 0
        self.frameTime = 0
        self.speed = 0.1
        self.sensativity = 2

        self.walk_offset_lookup = {
            1: 0,
            2: 90,
            3: 45,
            4: 180,
            6: 135,
            7: 90,
            8: 270,
            9: 315,
            11: 0,
            12: 225,
            13: 270,
            14: 180
        }

        
        
        self.mainLoop()


    def mainLoop(self):
        draw = True
        while draw:
            if not self.window:
                return
            if glfw.window_should_close(self.window) \
                or glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_ESCAPE) == GLFW_CONSTANTS.GLFW_PRESS:

                draw = False

            self.handleKeys()
            self.handleMouse()

            glfw.poll_events()

            self.scene.update(self.frameTime / 16.7)
            self.renderer.render(self.scene)

            #Timing
            self.calculateFramerate()
        self.quit()

    def handleKeys(self):

        combo = 0
        directionModifier = 0
        runBoost = 1
        crouchWalk = 1

        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_W) == GLFW_CONSTANTS.GLFW_PRESS:
            combo += 1
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_A) == GLFW_CONSTANTS.GLFW_PRESS:
            combo += 2
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_S) == GLFW_CONSTANTS.GLFW_PRESS:
            combo += 4
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_D) == GLFW_CONSTANTS.GLFW_PRESS:
            combo += 8
        
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_LEFT_SHIFT) == GLFW_CONSTANTS.GLFW_PRESS:
            runBoost = 1.5
        elif glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_LEFT_CONTROL) == GLFW_CONSTANTS.GLFW_PRESS:
            crouchWalk = 0.5

        

        if combo in self.walk_offset_lookup:
            directionModifier = self.walk_offset_lookup[combo]
            dPos = [
                self.speed * self.frameTime / 16.7 * np.cos(np.deg2rad(self.scene.player.theta + directionModifier)) * runBoost * crouchWalk,
                0,
                self.speed * -self.frameTime / 16.7 * np.sin(np.deg2rad(self.scene.player.theta + directionModifier)) * runBoost * crouchWalk
            ]
            self.scene.move_player(dPos)
            
        
        

    def handleMouse(self):

        (x,z) = glfw.get_cursor_pos(self.window)
        rate = self.frameTime / 16.7
        theta_increment = rate * ((SCREEN_WIDTH/2) - x) * self.sensativity
        phi_increment = rate * ((SCREEN_HEIGHT/2) - z) * self.sensativity
        self.scene.spin_player(theta_increment, phi_increment)
        glfw.set_cursor_pos(self.window, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    
    def calculateFramerate(self):

        self.currentTime = glfw.get_time()
        delta = self.currentTime - self.lastTime
        if (delta >= 1):
            framerate = max(1, int(self.numFrames / delta))
            glfw.set_window_title(self.window, f"Running at {framerate} fps.")
            self.lastTime = self.currentTime
            self.numFrames = -1
            self.frameTime = float(1000.0/max(1, framerate))
        self.numFrames += 1

    def checkCollision(self, move_direction, walls):
        for wall in self.scene.walls:
            pass


    def quit(self):
        self.renderer.quit()       

if __name__ == "__main__":
    window = initialize_glfw()
    myApp = App(window)


