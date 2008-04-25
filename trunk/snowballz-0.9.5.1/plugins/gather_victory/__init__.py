""" A simple plugin to setup a victory/defeat scenario based on who ever gathers
a certain amount of a certain resource first.

Add "gather_victory-v1" to the list of required_plugins (in your map) and add
a section something like the folling::

    [victory]
    resource_type = crystal
    amount = 20

That will grant victory to the first play that captures all regions and defeat
to any player that loses all of theirs.
"""

__version__ = 1

from events import *
import plugin
import data



def init(config):
    resource_type = config.get("victory", "resource_type")
    amount = config.getint("victory", "amount")
    return GatherVictoryPlugin(resource_type, amount)

class GatherVictoryPlugin(object):
    def __init__(self, resource_type, amount):
        self.resource_type = resource_type
        self.amount = amount

        connect(PENGUIN_UNLOADED, self.check_victory)

    def check_victory(self, penguin, resource_type):
        if resource_type == self.resource_type:
            amount = 0
            for b in data.buildings:
                if b.player == penguin.player:
                    amount += b.num_storage(self.resource_type)

            if amount >= self.amount:
                for p in data.players.values():
                    if p == penguin.player:
                        p.victory = True
                    else:
                        p.victory = False