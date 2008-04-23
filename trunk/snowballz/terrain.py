from __future__ import division
import random

import rabbyt
from rabbyt.vertexarrays import VertexArray, VertexArrayIndexes

import data


class Terrain(object):
    def __init__(self, image, ttype):
        self.vsize = (data.map.size[0]+1, data.map.size[1]+1)

        tsize = 256

        self.va = VertexArray("QUAD_STRIP")
        self.va.set_size(self.vsize[0]*self.vsize[1])
        for vy in xrange(self.vsize[1]):
            for vx in xrange(self.vsize[0]):
                try:
                    tile1 = data.map.tiles[(vx, vy)]
                    m = tile1.elevation*data.map.elevation_multiplier
                except KeyError:
                    m = 0

                vertex = self.va[vy*self.vsize[0]+vx]

                vertex.xy = vx*32, vy*32-m
                vertex.uv = vx*32/tsize, vy*32/tsize

                # Find the averate alpha from surrounding tiles
                total = 0
                num = 0
                for key in [(vx,vy), (vx-1, vy), (vx-1, vy-1), (vx, vy-1)]:
                    try:
                        tile = data.map.tiles[key]
                        if tile.type == ttype or ttype == "all":
                            total += 1
                        num += 1
                    except KeyError: pass
                alpha = total/num
                if alpha == .5:
                    alpha += random.random()*.8-.4
                vertex.alpha = alpha

                # Elevation shadows
                try:
                    tile1 = data.map.tiles[(vx, vy)]
                    tile2 = data.map.tiles[(vx-1, vy-1)]
                    d = (tile2.elevation - tile1.elevation) / 20
                    if d > 0:
                        d = 1-d
                    else:
                        d = 1.0
                except KeyError:
                    d = 1.0

                # Elevation highlights
                try:
                    tile1 = data.map.tiles[(vx, vy)]
                    tile2 = data.map.tiles[(vx+1, vy+1)]
                    d2 = (tile2.elevation - tile1.elevation) / 20
                    d2 = max(d2, 0)
                except KeyError:
                    d2 = 0.0
                d += d2
                d -= 0.1

                vertex.rgb = d, d, d

        self.row_indexes = []
        for y in range(self.vsize[1]-1):
            indexes = VertexArrayIndexes()
            for x in range(self.vsize[0]):
                indexes.append(y*self.vsize[0] + x)
                indexes.append((y+1)*self.vsize[0] + x)
            self.row_indexes.append(indexes)


    def draw(self, range_x, range_y):
        start_x = int(max(range_x[0]*2, 0))
        end_x = int(min(range_x[1]*2+1, self.vsize[1]*2))
        start_y = int(max(range_y[0], 0))
        end_y = int(min(range_y[1]+1,self.vsize[1]-1))

        self.va.enable_arrays()

        for y in range(start_y, end_y):
            self.row_indexes[y].render(self.va, start_x, end_x, False, False)

