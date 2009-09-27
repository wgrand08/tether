"""Copyright 2009:
    Isaac Carroll, Kevin Clement, Jon Handy, David Carroll, Daniel Carroll

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""


import pygame
import os

class MoonAudio:
    def __init__(self, client):
        self.client = client

    def music(self, chosen_song):
        if self.client.settings.play_music == True:
            pygame.mixer.music.load(os.path.join('data/music',chosen_song))
            pygame.mixer.music.play(-1)

    def sound(self, chosen_sound):
        if self.client.settings.play_sound == True:
            sound = pygame.mixer.Sound(os.path.join('data/sounds',chosen_sound))
            sound.play()

    def narrate(self, chosen_sound):
        if self.client.settings.play_sound == True: #todo: change to 'narrate'
            while pygame.mixer.get_busy(): #narrator must complete sentence before starting another
                placeholder = True
            sound = pygame.mixer.Sound(os.path.join('data/sounds/narrator',chosen_sound))
            sound.play()

    def end_music(self):
        pygame.mixer.music.fadeout(750)
