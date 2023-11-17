import time
import time

import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
import numpy as np
import random
import pygame
import sys
import os
import pygame.font

from player import Player
from graphicsengine import GraphicsEngine, SimpleComponent, Object, Light

from sound import Sound
import pygame as pg

from mazeGenerator import MazeGenerator
from enemy import Enemy
from key import Key

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

    def __init__(self, window) -> None:
        self.window = window
        # Enemy
        self.start_moving = True
        
        # Maze
        self.maze_size = 5
        self.cube_size = 5.0
        self.wall_height = 2.5

        self.mazeGenerator = MazeGenerator()
        self.maze = self.mazeGenerator.generate_maze(self.maze_size)
        print(self.maze)
        
        
        # self.teefys = [
        #     SimpleComponent(
        #         position= [2,2,0],
        #         eulers= [0,0,0],
        #         size=0
        #     ),
        #     SimpleComponent(
        #         position= [5,2,2],
        #         eulers= [0,0,0],
        #         size=0
        #     ),
        # ]

        '''
        Generate the walls, floors, and ceiling
        '''
        self.floors = []
        self.ceilings = []
        self.walls = []
        self.lights = []

        self.renderMaze()

        self.objects = []
        
    
        # Player
        #self.player = Player([self.player_y * 5, 2 , self.player_x * 5])
        self.player = Player([0, 2, 0])

        # Objective
        self.collected_key_count = 0
        self.keys, self.total_key_count = self.place_keys(3)
        self.updated_exit_position = False
        
        # Enemy
        self.enemy = Enemy([0, 0, 0])
        self.enemy.position = self.find_clear_spawn()
        self.enemies = [
            SimpleComponent(
                position=self.enemy.position,
                eulers= [0,0,0],
                size=8
            )
        ]

        # Exit sign, place the exit out of the view initially
        self.exit = SimpleComponent(
                position=[0,0,0],
                eulers= [0,0,0],
                size=3
            )
        self.lights.append(
                        Light(
                            position=[0,0,0],
                            color= [0.8, 0.8, 0.4],
                            intensity= 5
                        )
                    ) 
        self.exit.position = self.find_clear_spawn()
        self.exit.position[1] = 50
        self.lights[0].position = self.exit.position
        

        # Play the ambient sound
        self.sound = Sound()
        pg.mixer.music.play(-1)

        self.play = self.sound.play
        # Initialize footstep time
        self.last_footstep_time = 0
        self.footstep_delay = 0.5

        if self.check_immediate_collisions():
            print("Collision detected at the start position! Finding a new spawn location.")
            new_spawn_position = self.find_clear_spawn()
            if new_spawn_position:
                print(f"New spawn location found at: {new_spawn_position}")
                self.player.position = new_spawn_position
            else:
                print("No clear spawn location found. Please check your maze configuration.")

    def renderMaze(self):
        count = 0
        
        for i in range(len(self.maze)):
            for j in range(len(self.maze[i])):
                # Render a wall
                if self.maze[i][j] == 1:
                    # Wall position, and height
                    x = j * self.cube_size
                    y = self.wall_height
                    z = i * self.cube_size

                    wall_size = [self.cube_size, self.wall_height, self.cube_size]

                    wall_component = SimpleComponent(
                        position=[x, y, z],
                        eulers=[0, 0, 0],
                        size=wall_size
                    )

                    wall_component.calculate_bounding_box()
                    self.walls.append(wall_component)
                
                # Render floor and ceiling
                elif self.maze[i][j] == 0:
                    x_position = j * 5
                    z_position = i * 5

                    # Floor
                    self.floors.append(
                        SimpleComponent(
                            position=[x_position, 0, z_position],
                            eulers= [0, 0, 0],
                            size=0
                        )
                    )

                    # Ceiling
                    self.ceilings.append(
                        SimpleComponent(
                            position=[x_position, 5, z_position],
                            eulers= [0, 0 ,0],
                            size=0
                        )
                    )

                    # Lights
                    self.lights.append(
                        Light(
                            position=[x_position, 3, z_position],
                            color= [0.8, 0.7, 0.4],
                            intensity= 3
                        )
                    ) 

                    # count += 1  

    def update(self, rate):
        self.move_enemy_towards_player()
        self.enemies[0].position = self.enemy.position

        self.check_player_key_collision()
        if self.check_enemy_player_collision():
            print("You died!")
        camera_direction = self.player.get_camera_direction()
        for key in self.keys:
            key.update(.1, camera_direction)

        # Show the exit when all keys are collected
        if self.total_key_count == self.collected_key_count:
            if self.updated_exit_position == False:
                # Exit sign, add lights
                self.exit.position[1] = 1
                self.lights[0].position[1] = 3
                self.updated_exit_position == True
            
            # Move the exit up and down
            time_elapsed = time.time()
            vertical_offset = np.sin(time_elapsed) * 0.3 
            self.exit.position[1] = 1 + vertical_offset

            boundary = 2 # boundary threshold for exit
            if (
                self.exit.position[0] - boundary <= self.player.position[0] <= self.exit.position[0] + boundary and
                self.exit.position[2] - boundary <= self.player.position[2] <= self.exit.position[2] + boundary
            ):
                print("You win!")

        # OBJECT COLLISION #
        """ for teefy in self.teefys:
            vector = self.player.position - teefy.position
            distance = np.sqrt(vector[0] ** 2 + vector[2] ** 2)
            print(distance)
            if distance < 1:
                teefy.position[1] += 100 """
        
    def check_immediate_collisions(self):
        player_min_corner, player_max_corner = self.player.get_bounding_box()
        print(f"Player Bounding Box: Min {player_min_corner}, Max {player_max_corner}")
        for wall in self.walls:
            wall_min_corner = wall.min_corner
            wall_max_corner = wall.max_corner

            if self.check_collision(player_min_corner, player_max_corner, wall_min_corner, wall_max_corner):
                print(f"Immediate collision detected with wall at: {wall.position}")  # Debug print
                return True

        print("No immediate collisions detected.")  # Debug print
        return False
    
    def find_clear_spawn(self):
        potential_positions = [(i, j) for i in range(self.maze_size) for j in range(self.maze_size) if self.maze[i][j] == 0]
        random.shuffle(potential_positions)
        for i, j in potential_positions:
            x = j * self.cube_size
            y = 2
            z = i * self.cube_size

            if not self.check_collision_with_walls(x, y, z):
                print(f"Clear spawn found at maze coordinates ({i}, {j}), world coordinates ({x}, {y}, {z})")
                return [x, y, z]

        print("Unable to find a clear spawn position.")
        return None

    def check_collision_with_walls(self, x, y, z):
        player_min_corner, player_max_corner = self.player.get_bounding_box_at_position([x, y, z])
        for wall in self.walls:
            wall_min_corner = wall.min_corner
            wall_max_corner = wall.max_corner
            if self.check_collision(player_min_corner, player_max_corner, wall_min_corner, wall_max_corner):
                return True
        return False
    
    def check_enemy_player_collision(self):
        enemy_min_corner, enemy_max_corner = self.enemy.get_bounding_box()
        player_min_corner, player_max_corner = self.player.get_bounding_box()

        return self.check_collision(enemy_min_corner, enemy_max_corner, player_min_corner, player_max_corner)
    
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

    def move_enemy_towards_player(self):
        if self.start_moving == True: 
            player_position = np.array(self.player.position, dtype=np.float32)
            enemy_position = np.array(self.enemy.position, dtype=np.float32)

            direction_to_player = player_position - enemy_position

            for axis in range(3):
                if axis == 1:  # Skip the y-axis
                    continue

                step_size = 0.008 # ENEMY MOVEMENT SPEED
                temp_position = enemy_position.copy()
                temp_position[axis] += direction_to_player[axis] * step_size

                player_min_corner, player_max_corner = self.enemy.get_bounding_box_at_position(temp_position)

                collision = any(
                    self.check_collision(player_min_corner, player_max_corner, wall.min_corner, wall.max_corner)
                    for wall in self.walls
                )

                if not collision:
                    enemy_position[axis] += direction_to_player[axis] * step_size

            self.enemy.position = enemy_position

    def place_keys(self, number_of_keys, min_distance=15):
        keys = []
        potential_positions = [(i, j) for i in range(self.maze_size) for j in range(self.maze_size) if self.maze[i][j] == 0]
        random.shuffle(potential_positions)
        count = 0
        for i, j in potential_positions:
            if len(keys) >= number_of_keys:
                break  

            x = j * self.cube_size
            y = 2  
            z = i * self.cube_size


            if all(np.linalg.norm(np.array([x, y, z]) - np.array(key.position)) >= min_distance for key in keys):
                if not self.check_collision_with_walls(x, y, z):
                    keys.append(Key([x, y, z]))
                    print(f"Key placed at maze coordinates ({i}, {j}), world coordinates ({x}, {y}, {z})")
                    count += 1
        
        if len(keys) < number_of_keys:
            print("Unable to find sufficient clear positions for all keys.")
        
        return keys, count

    def check_player_key_collision(self):
        player_min, player_max = self.player.get_bounding_box()
        for key in self.keys:
            if key.collected:
                continue  

            key_min, key_max = key.get_bounding_box()
            if self.check_collision(player_min, player_max, key_min, key_max):
                self.handle_key_pickup(key)

    def handle_key_pickup(self, key):
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_E) == GLFW_CONSTANTS.GLFW_PRESS:
            key.collect()
            self.collected_key_count += 1
            print("Key collected!", self.collected_key_count)

class App:

    def __init__(self, window):
        
        self.window = window
        self.scene = Scene(window)
        self.renderer = GraphicsEngine(len(self.scene.lights))

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

            self.scene.update(self.frameTime / 16.7)  # Update the game scene
            self.renderer.render(self.scene)  # Render the game scene

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
            self.scene.start_moving = True
            self.scene.move_player(dPos)
            
            
            #self.scene.move_enemy(dPos)
            
        
        

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


    def quit(self):
        self.renderer.quit()

class StartMenu:
    def __init__(self, screen, frame_folder, font_path):  
        self.screen = screen
        self.frame_folder = frame_folder
        self.frames = self.load_frames()
        self.current_frame = 0
        self.running = True
        self.clock = pygame.time.Clock()
        self.fps = 2
        self.font_size = 60
        self.font = pygame.font.Font(font_path, self.font_size)  
        self.options = ["Start Game", "Settings", "Quit"]
        self.selected_option = 0  


    def load_frames(self):
        frames = []
        for filename in sorted(os.listdir(self.frame_folder)):
            if filename.endswith(".png"):
                frame_path = os.path.join(self.frame_folder, filename)
                image = pygame.image.load(frame_path)
                image = pygame.transform.scale(image, (800, 600))
                frames.append(image)
        return frames

    def update_frame(self):
        self.screen.blit(self.frames[self.current_frame], (0, 0))
        self.current_frame = (self.current_frame + 1) % len(self.frames)

    def show(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return self.options[self.selected_option]
                    elif event.key == pygame.K_w:  
                        self.selected_option = (self.selected_option - 1) % len(self.options)
                    elif event.key == pygame.K_s:  
                        self.selected_option = (self.selected_option + 1) % len(self.options)

            self.update_frame()
            self.draw_title()  
            self.draw_menu()   
            pygame.display.update()
            self.clock.tick(self.fps)

        return 'quit'
    
    def draw_title(self):
        title_surface = self.font.render("MazeGame", True, (255, 0, 0))  
        title_rect = title_surface.get_rect(center=(400, 50)) 
        self.screen.blit(title_surface, title_rect)

    def draw_menu(self):
        for i, option in enumerate(self.options):
            color = (255, 0, 0) if i == self.selected_option else (255, 255, 255)
            text_surface = self.font.render(option, True, color)
            text_rect = text_surface.get_rect(center=(400, 300 + i * 70))  
            self.screen.blit(text_surface, text_rect)

def start_game():
    window = initialize_glfw()
    myApp = App(window)

def main_menu():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))

    frame_folder = "../assets/MazeGameFrames/"  
    font_path = "../assets/fonts/DotGothic16-Regular.ttf"  
    menu = StartMenu(screen, frame_folder, font_path)  

    action = menu.show()
    pygame.quit()

    if action == 'Start Game':
        start_game()
    elif action == 'Quit':
        sys.exit()

if __name__ == "__main__":
    main_menu()