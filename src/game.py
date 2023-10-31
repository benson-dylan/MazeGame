import time
import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
import numpy as np

from player import Player
from graphicsengine import GraphicsEngine, SimpleComponent, Object, Light

from sound import Sound
import pygame as pg

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
        self.teefys = [
            SimpleComponent(
                position= [2,2,0],
                eulers= [0,0,0]
            ),
            SimpleComponent(
                position= [5,2,2],
                eulers= [0,0,0]
            ),
        ]
        self.floors = [
            SimpleComponent(
                position=[5,0,5],
                eulers=[0,0,0]
            ),
            SimpleComponent(
                position=[15,0,5],
                eulers=[0,0,0]
            ),
            SimpleComponent(
                position=[5,0,15],
                eulers=[0,0,0]
            ),
            SimpleComponent(
                position=[15,0,15],
                eulers=[0,0,0]
            ),
        ]
        self.walls = [
            SimpleComponent(
                position=[0,0,5],
                eulers=[0,0,0]
            ),
            SimpleComponent(
                position=[10,0,5],
                eulers=[0,0,0]
            ),
            SimpleComponent(
                position=[10,0,15],
                eulers=[0,0,0]
            ),
            SimpleComponent(
                position=[-5,0,5],
                eulers=[90,0,0]
            ),
        ]
        self.ceilings = [
            SimpleComponent(
                position=[5,5,5],
                eulers=[0,0,0]
            ),
            SimpleComponent(
                position=[5,5,5],
                eulers=[0,0,0]
            ),
            SimpleComponent(
                position=[15,5,15],
                eulers=[0,0,0]
            ),
            SimpleComponent(
                position=[5,5,15],
                eulers=[0,0,0]
            ),
        ]
        self.objects = []
        self.player = Player([5,2,5])
        self.lights = [
            Light(
                position = [5,4,5],
                color = [0.8, 0.7, 0.4],
                intensity = 10
            ),
            Light(
                position = [5,4,10],
                color = [0.8, 0.7, 0.4],
                intensity = 10
            ),
            Light(
                position = [10,4,10],
                color = [0.8, 0.7, 0.4],
                intensity = 10
            ),
            Light(
                position = [7,4,7],
                color = [0.8, 0.7, 0.4],
                intensity = 10
            ),
        ]

        self.sound = Sound()
        pg.mixer.music.play(-1)

        self.play = self.sound.play
        self.last_footstep_time = 0

    def update(self, rate):
        
        for object in self.objects:
            object.eulers[2] += 0.25 * rate
            if object.eulers[2] > 360:
                object.eulers[2] -= 360

        '''  # OBJECT COLLISION #
        for teefy in self.teefys:
            vector = self.player.position - teefy.position
            distance = np.sqrt(vector[0] ** 2 + vector[2] ** 2)
            print(distance)
            if distance < 1:
                teefy.position[1] += 100
        '''
    def move_player(self, dPos):
        
        dPos = np.array(dPos, dtype=np.float32)
        self.player.position += dPos

        # Delay between footstep sounds (in seconds)
        footstep_delay = 0.5  # Adjust this to your desired delay

        # Get the current time
        current_time = time.time()

        # Check if enough time has passed since the last footstep sound
        if current_time - self.last_footstep_time >= footstep_delay:
            self.play(self.sound.player_move)

            # Update the last footstep time
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



