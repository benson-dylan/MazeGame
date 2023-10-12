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
    sprites, sprite_size, sword, sword_sprite = load_sprites(horizontal_resolution)
    
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
            if sword_sprite < 1 and event.type == pg.MOUSEBUTTONDOWN:
                sword_sprite = 1
                
        frame_buffer = new_frame(player_x, player_y, player_rotation, frame_buffer, sky_texture, floor_texture, horizontal_resolution, half_vertical_resolution, scaling_factor, map_height, map_size,
                          wall_texture, exit_x, exit_y)
        surface = pg.surfarray.make_surface(frame_buffer * 255)
        
        enemies = sort_sprites(player_x, player_y, player_rotation, enemies, map_height, map_size, elapsed_time/5)
        surface, en = draw_sprites(surface, sprites, enemies, sprite_size, horizontal_resolution, half_vertical_resolution, ticks, sword, sword_sprite)

        surface = pg.transform.scale(surface, (800, 600))
        
        if int(sword_sprite) > 0:
            if sword_sprite == 1 and enemies[en][3] > 1 and enemies[en][3] < 10:
                enemies[en][0] = 0
                num_enemies = num_enemies - 1
            sword_sprite = (sword_sprite + elapsed_time * 5) % 4

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


    if not(map_height[int(x-0.2)][int(y)] or map_height[int(x+0.2)][int(y)] or
           map_height[int(x)][int(y-0.2)] or map_height[int(x)][int(y+0.2)]):
        player_x, player_y = x, y
        
    elif not(map_height[int(player_x-0.2)][int(y)] or map_height[int(player_x+0.2)][int(y)] or
             map_height[int(player_x)][int(y-0.2)] or map_height[int(player_x)][int(y+0.2)]):
        player_y = y
        
    elif not(map_height[int(x-0.2)][int(player_y)] or map_height[int(x+0.2)][int(player_y)] or
             map_height[int(x)][int(player_y-0.2)] or map_height[int(x)][int(player_y+0.2)]):
        player_x = x
        
    return player_x, player_y, player_rotation

def generate_maze(map_size):
    
    map_height = np.random.choice([0, 0, 0, 0, 1, 1], (map_size,map_size))
    map_height[0,:], map_height[map_size-1,:], map_height[:,0], map_height[:,map_size-1] = (1,1,1,1)

    player_x, player_y, player_rotation = 1.5, np.random.randint(1, map_size -1)+.5, np.pi/4
    x, y = int(player_x), int(player_y)
    map_height[x][y] = 0
    count = 0
    while True:
        testx, testy = (x, y)
        if np.random.uniform() > 0.5:
            testx = testx + np.random.choice([-1, 1])
        else:
            testy = testy + np.random.choice([-1, 1])
        if testx > 0 and testx < map_size -1 and testy > 0 and testy < map_size -1:
            if map_height[testx][testy] == 0 or count > 5:
                count = 0
                x, y = (testx, testy)
                map_height[x][y] = 0
                if x == map_size-2:
                    exit_x, exit_y = (x, y)
                    break
            else:
                count = count+1
    return player_x, player_y, player_rotation, map_height, exit_x, exit_y

@njit()
def new_frame(player_x, player_y, player_rotation, frame_buffer, sky_texture, floor_texture, horizontal_resolution, half_vertical_resolution, scaling_factor, map_height, map_size, wall_texture, exit_x, exit_y):
    for i in range(horizontal_resolution):
        rot_i = player_rotation + np.deg2rad(i/scaling_factor - 30)
        sin, cos, cos2 = np.sin(rot_i), np.cos(rot_i), np.cos(np.deg2rad(i/scaling_factor - 30))
        frame_buffer[i][:] = sky_texture[int(np.rad2deg(rot_i)*2%718)][:]

        x, y = player_x, player_y
        while map_height[int(x)%(map_size-1)][int(y)%(map_size-1)] == 0:
            x, y = x +0.01*cos, y +0.01*sin

        n = np.sqrt((x-player_x)**2+(y-player_y)**2)#abs((x - player_x)/cos)    
        h = int(half_vertical_resolution/(n*cos2 + 0.001))

        xx = int(x*3%1*99)        
        if x%1 < 0.02 or x%1 > 0.98:
            xx = int(y*3%1*99)
        yy = np.linspace(0, 3, h*2)*99%99

        shade = 0.3 + 0.7*(h/half_vertical_resolution)
        if shade > 1:
            shade = 1
            
        ash = 0 
        if map_height[int(x-0.33)%(map_size-1)][int(y-0.33)%(map_size-1)]:
            ash = 1
            
        if map_height[int(x-0.01)%(map_size-1)][int(y-0.01)%(map_size-1)]:
            shade, ash = shade*0.5, 0
            
        c = shade
        for k in range(h*2):
            if half_vertical_resolution - h +k >= 0 and half_vertical_resolution - h +k < 2*half_vertical_resolution:
                if ash and 1-k/(2*h) < 1-xx/99:
                    c, ash = 0.5*c, 0
                frame_buffer[i][half_vertical_resolution - h +k] = c*wall_texture[xx][int(yy[k])]
                if half_vertical_resolution+3*h-k < half_vertical_resolution*2:
                    frame_buffer[i][half_vertical_resolution+3*h-k] = c*wall_texture[xx][int(yy[k])]
                
        for j in range(half_vertical_resolution -h): #floor_texture
            n = (half_vertical_resolution/(half_vertical_resolution-j))/cos2
            x, y = player_x + cos*n, player_y + sin*n
            xx, yy = int(x*3%1*99), int(y*3%1*99)

            shade = 0.2 + 0.8*(1-j/half_vertical_resolution)
            if map_height[int(x-0.33)%(map_size-1)][int(y-0.33)%(map_size-1)]:
                shade = shade*0.5
            elif ((map_height[int(x-0.33)%(map_size-1)][int(y)%(map_size-1)] and y%1>x%1)  or
                  (map_height[int(x)%(map_size-1)][int(y-0.33)%(map_size-1)] and x%1>y%1)):
                shade = shade*0.5

            frame_buffer[i][half_vertical_resolution*2-j-1] = shade*(floor_texture[xx][yy]*2+frame_buffer[i][half_vertical_resolution*2-j-1])/3
            
            if int(x) == exit_x and int(y) == exit_y and (x%1-0.5)**2 + (y%1-0.5)**2 < 0.2:
                ee = j/(10*half_vertical_resolution)
                frame_buffer[i][j:2*half_vertical_resolution-j] = (ee*np.ones(3)+frame_buffer[i][j:2*half_vertical_resolution-j])/(1+ee)

    return frame_buffer

@njit()
def sort_sprites(player_x, player_y, player_rotation, enemies, map_height, map_size, elapsed_time):
    for en in range(len(enemies)):
        cos, sin = elapsed_time*np.cos(enemies[en][6]), elapsed_time*np.sin(enemies[en][6])
        enx, eny = enemies[en][0]+cos, enemies[en][1]+sin
        if (map_height[int(enx-0.1)%(map_size-1)][int(eny-0.1)%(map_size-1)] or
            map_height[int(enx-0.1)%(map_size-1)][int(eny+0.1)%(map_size-1)] or
            map_height[int(enx+0.1)%(map_size-1)][int(eny-0.1)%(map_size-1)] or
            map_height[int(enx+0.1)%(map_size-1)][int(eny+0.1)%(map_size-1)]):
            enx, eny = enemies[en][0], enemies[en][1]
            enemies[en][6] = enemies[en][6] + np.random.uniform(-0.5, 0.5)
        else:
            enemies[en][0], enemies[en][1] = enx, eny
        angle = np.arctan((eny-player_y)/(enx-player_x))
        if abs(player_x+np.cos(angle)-enx) > abs(player_x-enx):
            angle = (angle - np.pi)%(2*np.pi)
        angle2= (player_rotation-angle)%(2*np.pi)
        if angle2 > 10.5*np.pi/6 or angle2 < 1.5*np.pi/6:
            dir2p = ((enemies[en][6] - angle -3*np.pi/4)%(2*np.pi))/(np.pi/2)
            enemies[en][2] = angle2
            enemies[en][7] = dir2p
            enemies[en][3] = 1/np.sqrt((enx-player_x)**2+(eny-player_y)**2+1e-16)
            cos, sin = (player_x-enx)*enemies[en][3], (player_y-eny)*enemies[en][3]
            x, y = enx, eny
            for i in range(int((1/enemies[en][3])/0.05)):
                x, y = x +0.05*cos, y +0.05*sin
                if (map_height[int(x-0.02*cos)%(map_size-1)][int(y)%(map_size-1)] or
                    map_height[int(x)%(map_size-1)][int(y-0.02*sin)%(map_size-1)]):
                    enemies[en][3] = 9999
                    break
        else:
           enemies[en][3] = 9999

    enemies = enemies[enemies[:, 3].argsort()]
    return enemies

def spawn_enemies(number, map_height, msize):
    enemies = []
    for i in range(number):
        x, y = np.random.uniform(1, msize-2), np.random.uniform(1, msize-2)
        while (map_height[int(x-0.1)%(msize-1)][int(y-0.1)%(msize-1)] or
               map_height[int(x-0.1)%(msize-1)][int(y+0.1)%(msize-1)] or
               map_height[int(x+0.1)%(msize-1)][int(y-0.1)%(msize-1)] or
               map_height[int(x+0.1)%(msize-1)][int(y+0.1)%(msize-1)]):
            x, y = np.random.uniform(1, msize-1), np.random.uniform(1, msize-1)
        angle2p, invdist2p, dir2p = 0, 0, 0 # angle, inv dist, dir2p relative to player
        entype = np.random.choice([0,1]) # 0 zombie, 1 skeleton
        direction = np.random.uniform(0, 2*np.pi) # facing direction
        map_size = np.random.uniform(7, 10)
        enemies.append([x, y, angle2p, invdist2p, entype, map_size, direction, dir2p])

    return np.asarray(enemies)

def load_sprites(horizontal_resolution):
    sheet = pg.image.load('zombie_n_skeleton4.png').convert_alpha()
    sprites = [[], []]
    swordsheet = pg.image.load('sword1.png').convert_alpha() 
    sword = []
    for i in range(3):
        subsword = pg.Surface.subsurface(swordsheet,(i*800,0,800,600))
        sword.append(pg.transform.smoothscale(subsword, (horizontal_resolution, int(horizontal_resolution*0.75))))
        xx = i*32
        sprites[0].append([])
        sprites[1].append([])
        for j in range(4):
            yy = j*100
            sprites[0][i].append(pg.Surface.subsurface(sheet,(xx,yy,32,100)))
            sprites[1][i].append(pg.Surface.subsurface(sheet,(xx+96,yy,32,100)))

    sprite_size = np.asarray(sprites[0][1][0].get_size())*horizontal_resolution/800

    sword.append(sword[1]) # extra middle frame_buffer
    sword_sprite = 0 #current sprite for the sword
    
    return sprites, sprite_size, sword, sword_sprite

def draw_sprites(surface, sprites, enemies, sprite_size, horizontal_resolution, half_vertical_resolution, ticks, sword, sword_sprite):
    #enemies : x, y, angle2p, dist2p, type, map_size, direction, dir2p
    cycle = int(ticks)%3 # animation cycle for monsters
    for en in range(len(enemies)):
        if enemies[en][3] >  10:
            break
        types, dir2p = int(enemies[en][4]), int(enemies[en][7])
        cos2 = np.cos(enemies[en][2])
        scale = min(enemies[en][3], 2)*sprite_size*enemies[en][5]/cos2
        vert = half_vertical_resolution + half_vertical_resolution*min(enemies[en][3], 2)/cos2
        hor = horizontal_resolution/2 - horizontal_resolution*np.sin(enemies[en][2])
        spsurf = pg.transform.scale(sprites[types][cycle][dir2p], scale)
        surface.blit(spsurf, (hor,vert)-scale/2)

    swordpos = (np.sin(ticks)*10*horizontal_resolution/800,(np.cos(ticks)*10+15)*horizontal_resolution/800) # sword shake
    surface.blit(sword[int(sword_sprite)], swordpos)

    return surface, en-1

if __name__ == '__main__':
    main()
    pg.quit()
