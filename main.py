import pygame as pg
import numpy as np
from numba import njit

def main():
    pg.init()
    screen = pg.display.set_mode((800,600))
    running = True
    clock = pg.time.Clock()
    pg.mouse.set_visible(False)
    pg.event.set_grab(1)

    horizontal_resolution = 250 #horizontal resolution
    half_vertical_resolution = int(horizontal_resolution*0.375) #vertical resolution/2
    scaling_factor = horizontal_resolution/60 #scaling factor (60° fov)

    map_size = 25
    num_enemies = map_size*2 #number of enemies
    player_x, player_y, player_rotation, map_height, exit_x, exit_y = generate_maze(map_size)
    
    frame_buffer = np.random.uniform(0,1, (horizontal_resolution, half_vertical_resolution*2, 3))
    sky_texture = pg.surfarray.array3d(pg.transform.smoothscale(pg.image.load('skybox2.jpg'), (720, half_vertical_resolution * 2))) / 255
    floor_texture = pg.surfarray.array3d(pg.image.load('floor.jpg')) / 255
    wall_texture = pg.surfarray.array3d(pg.image.load('wall.jpg')) / 255
    sprites, sprite_size = load_sprites(horizontal_resolution)
    
    enemies = spawn_enemies(num_enemies, map_height, map_size)

    while running:
        ticks = pg.time.get_ticks() / 200
        elapsed_time = min(clock.tick() / 500, 0.3)

        if int(player_x) == exit_x and int(player_y) == exit_y:
            if num_enemies < map_size:
                print("You got out of the maze!")
                pg.time.wait(1000)
                running = False
            elif int(ticks % 10 + 0.9) == 0:
                print("There is still work to do...")

        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                running = False
                
        frame_buffer = new_frame(player_x, player_y, player_rotation, frame_buffer, sky_texture, floor_texture, horizontal_resolution, half_vertical_resolution, scaling_factor, map_height, map_size,
                          wall_texture, exit_x, exit_y)
        surface = pg.surfarray.make_surface(frame_buffer * 255)
        
        enemies = update_enemies(player_x, player_y, player_rotation, enemies, map_height, map_size, elapsed_time/5)
        surface, en = draw_sprites(surface, sprites, enemies, sprite_size, horizontal_resolution, half_vertical_resolution, ticks)

        surface = pg.transform.scale(surface, (800, 600))

        screen.blit(surface, (0, 0))
        pg.display.update()
        fps = int(clock.get_fps())
        pg.display.set_caption("Enemies remaining: " + str(num_enemies) + " - FPS: " + str(fps))
        player_x, player_y, player_rotation = movement(pg.key.get_pressed(), player_x, player_y, player_rotation, map_height, elapsed_time)

def movement(pressed_keys, player_x, player_y, player_rotation, map_height, elapsed_time):
    x, y, diag, diag = player_x, player_y, player_rotation, 0

    if pg.mouse.get_focused():
        mouse_movement = pg.mouse.get_rel()
        player_rotation = player_rotation + np.clip((mouse_movement[0]) / 200, -0.2, .2)

    if pressed_keys[pg.K_UP] or pressed_keys[ord('w')]:
        x, y, diag = x + elapsed_time * np.cos(player_rotation), y + elapsed_time * np.sin(player_rotation), 1

    elif pressed_keys[pg.K_DOWN] or pressed_keys[ord('s')]:
        x, y, diag = x - elapsed_time * np.cos(player_rotation), y - elapsed_time * np.sin(player_rotation), 1
        
    if pressed_keys[pg.K_LEFT] or pressed_keys[ord('a')]:
        elapsed_time = elapsed_time / (diag + 1)
        x, y = x + elapsed_time * np.sin(player_rotation), y - elapsed_time * np.cos(player_rotation)
        
    elif pressed_keys[pg.K_RIGHT] or pressed_keys[ord('d')]:
        elapsed_time = elapsed_time / (diag + 1)
        x, y = x - elapsed_time * np.sin(player_rotation), y + elapsed_time * np.cos(player_rotation)


    if not(map_height[int(x - 0.2)][int(y)] or map_height[int(x + 0.2)][int(y)] or
           map_height[int(x)][int(y - 0.2)] or map_height[int(x)][int(y + 0.2)]):
        player_x, player_y = x, y
        
    elif not(map_height[int(player_x - 0.2)][int(y)] or map_height[int(player_x + 0.2)][int(y)] or
             map_height[int(player_x)][int(y - 0.2)] or map_height[int(player_x)][int(y + 0.2)]):
        player_y = y
        
    elif not(map_height[int(x - 0.2)][int(player_y)] or map_height[int(x + 0.2)][int(player_y)] or
             map_height[int(x)][int(player_y - 0.2)] or map_height[int(x)][int(player_y + 0.2)]):
        player_x = x
        
    return player_x, player_y, player_rotation

def generate_maze(map_size):
    
    map_height = np.random.choice([0, 0, 0, 0, 1, 1], (map_size, map_size))
    map_height[0, :], map_height[map_size-1, :], map_height[:, 0], map_height[:, map_size-1] = (1, 1, 1, 1)

    player_x, player_y, player_rotation = 1.5, np.random.randint(1, map_size -1) + .5, np.pi / 4
    x, y = int(player_x), int(player_y)
    map_height[x][y] = 0
    count = 0

    while True:
        test_x, test_y = (x, y)

        if np.random.uniform() > 0.5:
            test_x = test_x + np.random.choice([-1, 1])
        else:
            test_y = test_y + np.random.choice([-1, 1])

        if test_x > 0 and test_x < map_size -1 and test_y > 0 and test_y < map_size -1:
            if map_height[test_x][test_y] == 0 or count > 5:
                count = 0
                x, y = (test_x, test_y)
                map_height[x][y] = 0
                
                if x == map_size-2:
                    exit_x, exit_y = (x, y)
                    break
            else:
                count = count+1
    return player_x, player_y, player_rotation, map_height, exit_x, exit_y

@njit()
def new_frame(player_x, player_y, player_rotation, frame_buffer, sky_texture, floor_texture, horizontal_resolution, half_vertical_resolution, scaling_factor, map_height, map_size, wall_texture, exit_x, exit_y):
    for column in range(horizontal_resolution):
        # Calculate the current rotation angle
        rotation_angle = player_rotation + np.deg2rad(column / scaling_factor - 30)
        sin = np.sin(rotation_angle)
        cos = np.cos(rotation_angle)
        cos2 = np.cos(np.deg2rad(column / scaling_factor - 30))
        frame_buffer[column][:] = sky_texture[int(np.rad2deg(rotation_angle) * 2 % 718)][:]

        x = player_x
        y = player_y
        # Cast a ray until it hits a wall
        while map_height[int(x) % (map_size - 1)][int(y) % (map_size - 1)] == 0:
            x, y = x + 0.01 * cos, y + 0.01 * sin

        # Calculate the height of the wall column
        distance = np.sqrt((x-player_x) ** 2 + (y - player_y) ** 2)    
        height = int(half_vertical_resolution/(distance*cos2 + 0.001))

        # Determine which part of the wall texture to use
        texture_x = int(x * 3 % 1 * 99)        
        if x % 1 < 0.02 or x % 1 > 0.98:
            texture_x = int(y * 3 % 1 * 99)

        texture_y = np.linspace(0, 3, height * 2) * 99 % 99

        # Calculate shading based on wall height
        shading = 0.3 + 0.7 * (height / half_vertical_resolution)
        if shading > 1:
            shading = 1
        
        # Handle transparent walls (ash) and shading
        ash = 0
        if map_height[int(x - 0.33) % (map_size - 1)][int(y - 0.33) % (map_size - 1)]:
            ash = 1
            
        if map_height[int(x - 0.01) % (map_size - 1)][int(y - 0.01) % (map_size - 1)]:
            shading = shading * 0.5
            ash = 0
        
        # Render the wall texture
        color = shading
        for k in range(height * 2):
            if half_vertical_resolution - height + k >= 0 and half_vertical_resolution - height + k < 2 * half_vertical_resolution:
                if ash and 1 - k / (2 * height) < 1 - texture_x / 99:
                    color, ash = 0.5 * color, 0
                frame_buffer[column][half_vertical_resolution - height + k] = color * wall_texture[texture_x][int(texture_y[k])]
                if half_vertical_resolution + 3 * height - k < 2 * half_vertical_resolution:
                    frame_buffer[column][half_vertical_resolution + 3 * height - k] = color * wall_texture[texture_x][int(texture_y[k])]

                
        # Render the floor and apply shading
        for row in range(half_vertical_resolution - height):
            distance = (half_vertical_resolution / (half_vertical_resolution - row)) / cos2
            x, y = player_x + cos * distance, player_y + sin * distance
            texture_x, texture_y = int(x * 3 % 1 * 99), int(y * 3 % 1 * 99)

            shading = 0.2 + 0.8 * (1 - row / half_vertical_resolution)
            if map_height[int(x - 0.33) % (map_size - 1)][int(y - 0.33) % (map_size - 1)]:
                shading = shading * 0.5
                
            elif (map_height[int(x - 0.33) % (map_size - 1)][int(y) % (map_size - 1)] and y % 1 > x % 1) or \
                 (map_height[int(x) % (map_size - 1)][int(y - 0.33) % (map_size - 1)] and x % 1 > y % 1):
                shading = shading * 0.5

            frame_buffer[column][2 * half_vertical_resolution - row - 1] = shading * (floor_texture[texture_x][texture_y] * 2 + frame_buffer[column][2 * half_vertical_resolution - row - 1]) / 3

            # Check if the player is near the exit and apply a special effect
            if int(x) == exit_x and int(y) == exit_y and (x % 1 - 0.5) ** 2 + (y % 1 - 0.5) ** 2 < 0.2:
                exit_effect = row / (10 * half_vertical_resolution)
                frame_buffer[column][row:2 * half_vertical_resolution - row] = (exit_effect * np.ones(3) + frame_buffer[column][row:2 * half_vertical_resolution - row]) / (1 + exit_effect)

    return frame_buffer

@njit()
def update_enemies(player_x, player_y, player_rotation, enemies, map_height, map_size, elapsed_time):
    for enemy in range(len(enemies)):
        # Calculate the new position based on enemy movement
        cos, sin = elapsed_time * np.cos(enemies[enemy][6]), elapsed_time * np.sin(enemies[enemy][6])
        new_x, new_y = enemies[enemy][0] + cos, enemies[enemy][1] + sin

        # Check for collision with walls
        if (map_height[int(new_x - 0.1) % (map_size - 1)][int(new_y - 0.1) % (map_size - 1)] or
            map_height[int(new_x - 0.1) % (map_size - 1)][int(new_y + 0.1) % (map_size - 1)] or
            map_height[int(new_x + 0.1) % (map_size - 1)][int(new_y - 0.1) % (map_size - 1)] or
            map_height[int(new_x + 0.1) % (map_size - 1)][int(new_y + 0.1) % (map_size - 1)]):
            # Revert to the original position and change direction randomly
            new_x, new_y = enemies[enemy][0], enemies[enemy][1]
            enemies[enemy][6] = enemies[enemy][6] + np.random.uniform(-0.5, 0.5)
        else:
            enemies[enemy][0], enemies[enemy][1] = new_x, new_y

        # Calculate the angle and direction relative to the player
        angle = np.arctan2(new_y - player_y, new_x - player_x)
        if abs(player_x + np.cos(angle) - new_x) > abs(player_x - new_x):
            angle = (angle - np.pi) % (2 * np.pi)

        angle_difference = (player_rotation - angle) % (2 * np.pi)

        if angle_difference > 10.5 * np.pi / 6 or angle_difference < 1.5 * np.pi / 6:
            # Calculate direction and other properties
            direction_to_player = ((enemies[enemy][6] - angle - 3 * np.pi / 4) % (2 * np.pi)) / (np.pi / 2)
            enemies[enemy][2] = angle_difference
            enemies[enemy][7] = direction_to_player
            enemies[enemy][3] = 1 / np.sqrt((new_x - player_x) ** 2 + (new_y - player_y) ** 2 + 1e-16)

            # Check for wall collisions along the path to the player
            cos, sin = (player_x - new_x) * enemies[enemy][3], (player_y - new_y) * enemies[enemy][3]
            x, y = new_x, new_y
            for i in range(int((1 / enemies[enemy][3]) / 0.05)):
                x, y = x + 0.05 * cos, y + 0.05 * sin
                if (map_height[int(x - 0.02 * cos) % (map_size - 1)][int(y) % (map_size - 1)] or
                    map_height[int(x) % (map_size - 1)][int(y - 0.02 * sin) % (map_size - 1)]):
                    enemies[enemy][3] = 9999
                    break
        else:
            enemies[enemy][3] = 9999

    # Sort the enemies by distance to the player
    enemies = enemies[enemies[:, 3].argsort()]
    return enemies

def spawn_enemies(number, map_height, msize):
    enemies = []
    for i in range(number):
        x, y = np.random.uniform(1, msize - 2), np.random.uniform(1, msize - 2)
        while (map_height[int(x-0.1)%(msize-1)][int(y-0.1)%(msize-1)] or
               map_height[int(x-0.1)%(msize-1)][int(y+0.1)%(msize-1)] or
               map_height[int(x+0.1)%(msize-1)][int(y-0.1)%(msize-1)] or
               map_height[int(x+0.1)%(msize-1)][int(y+0.1)%(msize-1)]):
            x, y = np.random.uniform(1, msize-1), np.random.uniform(1, msize-1)

        angle_to_player, inverse_distance_to_player, direction_to_player = 0, 0, 0 # angle, inv dist, direction_to_player relative to player
        entype = np.random.choice([0,1]) # 0 zombie, 1 skeleton
        direction = np.random.uniform(0, 2*np.pi) # facing direction
        map_size = np.random.uniform(7, 10)
        enemies.append([x, y, angle_to_player, inverse_distance_to_player, entype, map_size, direction, direction_to_player])

    return np.asarray(enemies)

def load_sprites(horizontal_resolution):
    zombie_skeleton_sheet  = pg.image.load('zombie_n_skeleton4.png').convert_alpha()
    sprites = [[], []]

    for i in range(3):
        xx = i*32
        sprites[0].append([])
        sprites[1].append([])
        for j in range(4):
            yy = j*100
            sprites[0][i].append(pg.Surface.subsurface(zombie_skeleton_sheet ,(xx,yy,32,100)))
            sprites[1][i].append(pg.Surface.subsurface(zombie_skeleton_sheet ,(xx+96,yy,32,100)))

    sprite_size = np.asarray(sprites[0][1][0].get_size())*horizontal_resolution/800

    
    return sprites, sprite_size

def draw_sprites(surface, sprites, enemies, sprite_size, horizontal_resolution, half_vertical_resolution, ticks):
    # Animation cycle for monsters
    cycle = int(ticks) % 3
    for en in range(len(enemies)):
        if enemies[en][3] >  10:
            break
        
        types = int(enemies[en][4])
        direction_to_player = int(enemies[en][7])
        cos2 = np.cos(enemies[en][2])
        scale = min(enemies[en][3], 2) * sprite_size * enemies[en][5] / cos2
        vert = half_vertical_resolution + half_vertical_resolution * min(enemies[en][3], 2) / cos2
        hor = horizontal_resolution / 2 - horizontal_resolution * np.sin(enemies[en][2])
        sp_surf = pg.transform.scale(sprites[types][cycle][direction_to_player], scale)
        surface.blit(sp_surf, (hor, vert) - scale / 2)

    return surface, en-1

if __name__ == '__main__':
    main()
    pg.quit()
