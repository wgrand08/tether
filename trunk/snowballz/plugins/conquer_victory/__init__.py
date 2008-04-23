""" A simple plugin to setup a victory/defeat scenario based on conquest.

Add "conquer_victory-v1" to the list of required_plugins (in your map) and add
a section something like the folling::

    [victory]
    to_win = all
    to_lose = 0

That will grant victory to the first play that captures all regions and defeat
to any player that loses all of theirs.
"""

__version__ = 1

from events import *
import plugin
import data



def init(config):
    to_win = config.get("victory", "to_win")
    if to_win.isdigit():
        to_win = int(to_win)
    to_lose = config.getint("victory", "to_lose")
    return ConquerVictoryPlugin(to_win, to_lose)

class ConquerVictoryPlugin(object):
    def __init__(self, to_win, to_lose):
        self.to_win = to_win
        self.to_lose = to_lose

        connect(REGION_TAKEOVER, self.check_victory)

    def check_victory(self, region, old_player):
        regions = {}
        num_regions = 0
        for r in data.map.regions.values():
            if r.igloo:
                num_regions += 1
                if not r.player in regions:
                    regions[r.player] = 1
                else:
                    regions[r.player] += 1

        if self.to_win == "all":
            self.to_win = num_regions

        for p in data.players.values():
            if p in regions:
                if regions[p] == 0:
                    p.victory = False
                elif regions[p] >= self.to_win:
                    p.victory = True
                    for pl in data.players.values():
                        if pl == p: continue
                        pl.victory = False
            else:
                p.victory = False