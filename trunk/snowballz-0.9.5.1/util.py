import os
animations = {}

def gen_walk_animations():
    # Must be called before units are created!
num_frames = 10
directions = [(0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1), (1,0), (1,1)]
for d in directions:
    if d == (0,1):
        frame_add = 0
    if d == (-1,1):
        frame_add = 20
    if d == (-1,0):
        frame_add = 40
    if d == (-1,-1):
        frame_add = 60
    if d == (0,-1):
        frame_add = 80
    if d == (1,-1):
        frame_add = 100
    if d == (1,0):
        frame_add = 120
    if d == (1,1):
        frame_add = 150
    name = "walk%i%i" % d
    for i in range(num_frames):
        file = "%04d.png" % (i+1+frame_add)
        fullpath = os.path.join("data", "units", "penguin", file)
        print fullpath