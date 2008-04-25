import os
import pygame
import rabbyt.fonts


class Font:
    def __init__ (self, facename, pixel_height, invert_y=False):
        # We haven't yet allocated textures or display lists
        facename = os.path.join(*facename.split("/"))

        self.invert_y = invert_y
        self.m_font_height = pixel_height

        f = pygame.font.Font(facename, pixel_height)
        self.font = rabbyt.fonts.Font(f)
        self.sprite = rabbyt.fonts.FontSprite(self.font, "")

        if invert_y:
            for char in self.font.alphabet:
                l, t, r, b = self.font.coords[char]
                self.font.coords[char] = l, b, r, t


    def render(self, x, y, string, color=(1,1,1)):
        self.sprite.red = color[0]
        self.sprite.green = color[1]
        self.sprite.blue = color[2]
        if len(color) == 4:
            self.sprite.alpha = color[3]
        else:
            self.sprite.alpha = 1

        self.sprite.text = string
        self.sprite.xy = x, y+self.m_font_height
        self.sprite.render()
