import pygame as pg

MAX_SOUND_CHANNELS = 10

class Sound:
    def __init__(self):
        pg.mixer.init()
        pg.mixer.set_num_channels(MAX_SOUND_CHANNELS)
        self.channel = 0
        self.path = "../assets/sounds/"
       
        self.player_move = self.load('footstep.wav')

        pg.mixer.music.load(self.path + 'ambient.mp3')
        pg.mixer.music.set_volume(0.1)

    def load(self, file_name, volume=0.4):
        sound = pg.mixer.Sound(self.path + file_name)
        sound.set_volume(volume)
        return sound

    def play(self, sound):
        pg.mixer.Channel(self.channel).play(sound)
        self.channel += 1
        if self.channel == MAX_SOUND_CHANNELS:
            self.channel = 0
