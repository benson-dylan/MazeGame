import pygame as pg
def load_image(filename):
    img = pg.image.load(filename)
    img_data = pg.image.tostring(img, "RGBA")
    w, h = img.get_rect().size
    return img_data, w, h