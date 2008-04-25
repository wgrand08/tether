from building import Building
import pygame

class LandObstruction(Building):
    size = 8
    range = 0
    demand = {}
    capacity = 0
    cost = {}
    name = "landobstruction"
    strength = 0

    def __init__(self, pos, name):
        Building.__init__(self, pos, None, name, construction=100)

    def draw_fluf(self):
        pass