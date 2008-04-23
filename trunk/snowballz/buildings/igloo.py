from building import Building
import pygame
import data

class Igloo(Building):
    size = 4
    range = 10
    name = "igloo"
    image_name = "igloo"
    smoke_start = (101,30)

    # in milliseconds.
    takeover_time = 30000


    def in_building(self, unit):
        # FIXME: this does NOT support multiple enemies in an igloo!
        if self.jeopardy:
            if unit.player != self.player:
                if self.jeopardy_count+self.takeover_time <= data.get_ticks():
                    # Takeover!
                    self.region.player = unit.player
                    self.jeopardy = False
        else:
            if unit.warmth == unit.max_warmth:
                # Unit is warm.
                self.units_in_building.remove(unit)
                unit.state = "stray"
                unit.go_to_building = None
                return (-1,-1)
            if unit.counter+120000/unit.warmth <= data.get_ticks():
                # Exit building.
                if unit.warmth > unit.max_warmth-2:
                    unit.max_warmth = 10
                    unit.snowballs = 2
                    return self.unit_exit(unit)
                elif self.num_storage("fish") > 0:
                    unit.warmth = unit.max_warmth
                    self.remove_storage("fish")
                    unit.snowballs = 2
                    return self.unit_exit(unit)
                elif unit.counter+200000/unit.warmth <= data.get_ticks():
                    unit.warmth = unit.max_warmth
                    unit.snowballs = 2
                    return self.unit_exit(unit)



    def unit_enter(self, unit):
        if unit.player != self.player:
            self.player_taking_over = unit.player
            self.jeopardy = True
            self.jeopardy_count = data.get_ticks()

        if unit.warmth > 4:
            if self.jeopardy and unit.player == self.player and unit.type == "snowballer":
                # Building saved!
                self.jeopardy = False

            # Kick out enemy unit(s)
            if unit.type == "snowballer":
                units_to_kick = set()
                for u in self.units_in_building:
                    if u.player != unit.player and u.player != self.player:
                        units_to_kick.add(u)
                for u in units_to_kick:
                    u.warmth = 4
                    self.unit_exit(u)

        if unit.player == self.player:
            unit.igloo = self


    def unit_exit(self,unit):
        unit.state = "stray"
        self.units_in_building.remove(unit)
        unit.go_to_building = None
        return (-1,-1)


    def can_enter(self, unit):
        if unit.player != self.player and unit.warmth >= 5:
            return True
        elif unit.player == self.player:
            return True
