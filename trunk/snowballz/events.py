PENGUIN_MOVE = 1
PENGUIN_RELOAD = 2
PENGUIN_HIT = 3
PENGUIN_DIRECT_HIT = 4
PENGUIN_FROZEN = 5
PENGUIN_GATHERED = 6
PENGUIN_UNLOADED = 7

# When this event is fired, the first param is the region in question and the
# second param is the player that it used to belong to.
REGION_TAKEOVER = 8

connects = {}

def connect(event, callback):
    if not connects.has_key(event):
        connects[event] = []
    connects[event].append(callback)

def disconnect(event, callback):
    connects[event].remove(callback)

def fire(event, *params):
    if not connects.has_key(event):
        connects[event] = []

    cs = connects[event]
    for c in cs:
        c(*params)