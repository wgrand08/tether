from __future__ import division
import data
from OpenGL.GL import *

class MiniMap:
    def __init__(self):
        self.scale = min(data.view.h/data.map.size[0], data.view.w/data.map.size[1])
        self.draw_x = -(self.scale*data.map.size[0]-data.view.w)//2
        self.draw_y = (self.scale*data.map.size[1]-data.view.h)//2+data.view.h


    def draw(self):
        glDisable(GL_TEXTURE_2D)
        glPushMatrix()

        glTranslatef(self.draw_x, self.draw_y, 0)

        # Scale minimap to fill screen height
        glScalef(self.scale,self.scale,1)

        # Draw minimap bg.
        glColor4f(0,0,0, 0.3)

        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(data.map.size[0], 0)
        glVertex2f(data.map.size[0], -data.map.size[1])
        glVertex2f(0, -data.map.size[1])
        glEnd()
        glColor4f(1,1,1,1)

        glPointSize(4)
        # Draw buildings on minimap.
        glBegin(GL_POINTS)
        for b in data.buildings:
            if b.player:
                if b.player:
                    glColor4f(*b.player.glcolor+[1])
                else:
                    glColor4f(1,1,1, 1)
                glVertex2i(b.x, -b.y)
        glEnd()

        # Draw penguins on minimap.
        glPointSize(2)
        glBegin(GL_POINTS)
        for u in data.units:
            if u.igloo.player:
                glColor3f(*u.igloo.player.glcolor)
            else:
                glColor3f(1,1,1)
            glVertex2i(u.x, -u.y)
        glEnd()

        for d in data.map._dynamic_objects:
            if d.minimapimage and not d.hidden:
                d.doanimate()
                d.minimapicon.render()

        # Draw screen on minimap.
        glColor4f(0, 0.3, 0.3, 0.3)
        x = data.view.x/32
        y = data.view.y/32

        glTranslatef(x, -y, 0)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(data.view.scale_w/32, 0)
        glVertex2f(data.view.scale_w/32, -data.view.scale_h/32)
        glVertex2f(0, -data.view.scale_h/32)
        glEnd()
        glColor4f(1,1,1,1)

        glPopMatrix()



    def pos_to_mappos(self, cx, cy):
        cx -= self.scale*data.view.scale_w//32//2
        cy -= self.scale*data.view.scale_h//32//2

        # Get the position of the mouse relative to the minimap.
        px = cx - self.draw_x
        py = cy - self.draw_y

        py += self.scale*data.map.size[1]

        return px*32//self.scale, py*32//self.scale
