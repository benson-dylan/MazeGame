import pygame as pg

def movement_handling():
    pass

def handle_camera_movement(camera, keys):
    if keys[pg.K_w]:
         camera.move_forward()
    if keys[pg.K_s]:
         camera.move_backward()
    if keys[pg.K_a]:
         camera.move_left()
    if keys[pg.K_d]:
         camera.move_right()

def handle_camera_target(camera, mouse):
     camera.update_target(mouse[0], mouse[1])


def escape_game(event):
    if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                quit()

    