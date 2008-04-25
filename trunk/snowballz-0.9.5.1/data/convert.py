import os, Image, math

num_frames = 10
directions = [(0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1), (1,0), (1,1)]

w = num_frames*len(directions)*32
w = 2 ** math.ceil(math.log(w, 2))
anim = Image.new("RGBA", (512,256))

for dc in xrange(len(directions)):
    d = directions[dc]
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
    #name = "walk%i%i" % d

    for i in xrange(num_frames):
        file = "%04d.png" % (i+1+frame_add)
        image = Image.open(file)
        anim.paste(image, (i*32,dc*32))

    file = "idle/i%i%i.png" % d
    image = Image.open(file)
    anim.paste(image, (10*32,dc*32))
anim.save("walk.png", "PNG")