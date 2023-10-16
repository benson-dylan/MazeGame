# Modules
import pygame as pg
import numpy as np
from numba import njit
from pygame import font

# Dependencies
from constants import *
from player_movement import movement
from maze_generator import generate_maze
from frame_renderer import new_frame
from enemy_logic import update_enemies, spawn_enemies, check_player_enemy_collision
from sprites import load_sprites, draw_sprites

def main():
    pg.init()
    pg.font.init()
    font = pg.font.Font('PixelifySans-Bold.ttf', 50)
    screen = pg.display.set_mode(RESOLUTION)
    running = True
    clock = pg.time.Clock()
    pg.mouse.set_visible(False)
    pg.event.set_grab(1)

    # Generate the maze
    player_x, player_y, player_rotation, maze, exit_x, exit_y = generate_maze()
    
    # Load the textures and sprites
    frame_buffer = np.random.uniform(0,1, (HORIZONTAL_RESOLUTION, HALF_VERTICAL_RESOLUTION*2, 3))
    sky_texture = pg.surfarray.array3d(pg.transform.smoothscale(pg.image.load('resources/textures/sky.png'), (720, HALF_VERTICAL_RESOLUTION * 2))) / 255
    floor_texture = pg.surfarray.array3d(pg.image.load('resources/textures/floor.jpg')) / 255
    wall_texture = pg.surfarray.array3d(pg.image.load('resources/textures/wall.png')) / 255
    sprites, sprite_size = load_sprites()
    
    # Spawn the enemies at different locations
    enemies = spawn_enemies(NUM_ENEMIES, maze)

    # Main render loop
    while running:
        ticks = pg.time.get_ticks() / 200
        elapsed_time = min(clock.tick() / 500, 0.3)

        # Check if the player has reached the exit
        if int(player_x) == exit_x and int(player_y) == exit_y:
            print("You got out of the maze!")
            
        # Exit handling
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                running = False
        
        # Update the frame buffer
        frame_buffer = new_frame(player_x, player_y, player_rotation, frame_buffer, sky_texture, floor_texture, maze, wall_texture, exit_x, exit_y)
        surface = pg.surfarray.make_surface(frame_buffer * 255)
        
        # Update enemies and check for collisions
        enemies = update_enemies(player_x, player_y, player_rotation, enemies, maze, elapsed_time/5)
        surface, en = draw_sprites(surface, sprites, enemies, sprite_size, ticks)

        # Collision handling
        if check_player_enemy_collision(player_x, player_y, enemies):
            restart = death_screen(screen)
            if restart:
                # Reset game state
                player_x, player_y, player_rotation, maze, exit_x, exit_y = generate_maze()
                enemies = spawn_enemies(NUM_ENEMIES, maze)
                continue
            else:
                running = False
                break
        surface = pg.transform.scale(surface, RESOLUTION)

    # Display the surface on the screen
        screen.blit(surface, (0, 0))
        pg.display.update()
        fps = int(clock.get_fps())
        pg.display.set_caption("Enemies remaining: " + str(NUM_ENEMIES) + " - FPS: " + str(fps))
        player_x, player_y, player_rotation = movement(pg.key.get_pressed(), player_x, player_y, player_rotation, maze, elapsed_time)



def death_screen(screen):
    font = pg.font.Font('PixelifySans-Bold.ttf', 64)
    message = font.render("You Died!", True, (255, 0, 0))
    message_rect = message.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))

    instruction_font = pg.font.Font(None, 32)
    instruction = instruction_font.render("Press 'R' to Restart or 'Q' to Quit", True, (255, 255, 255))
    instruction_rect = instruction.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

    screen.blit(message, message_rect)
    screen.blit(instruction, instruction_rect)
    pg.display.flip()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            if event.type == pg.KEYDOWN:
                if event.key == 114: 
                    return True
                elif event.key == 113:
                    return False




if __name__ == '__main__':
    main()
    pg.quit()
