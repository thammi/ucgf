#!/usr/bin/env python
###############################################################################
##
## Copyright (C) 2010  Thammi
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU Affero General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Affero General Public License for more details.
##
## You should have received a copy of the GNU Affero General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
##
###############################################################################

from warnings import warn

from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

import ucgf

def face_item(l):
    raw = [int(i) if i else None for i in l.split('/')]
    return tuple(raw + [None] * (3 - len(raw)))

class GraphNode:

    def __init__(self, vertex):
        self.vertex = vertex

        self.faces = set()
        self.neighbors = set()

class ObjObject:

    def __init__(self, file_name, color=(1, 0, 1)):
        self.color = color

        self.vertices = vertices = []
        self.normals = normals = []
        self.texture = texture = []
        self.faces = faces = []
        
        inp = open(file_name)

        actions = {
                'v': lambda l: vertices.append(tuple(float(i) for i in l)),
                'vn': lambda l: normals.append(tuple(float(i) for i in l)),
                'vt': lambda l: texture.append(tuple(float(i) for i in l)),
                'f': lambda l: faces.append(tuple(face_item(i) for i in l)),
                }

        for line in inp:
            if line[0] != '#' and not line.isspace():
                args = line.split()

                cmd = args[0]

                if cmd in actions:
                    actions[args[0]](args[1:])
                else:
                    warn("Unknown command: " + cmd)

    def gl_init(self):
        self.gl_list = ucgf.list_render(self.raw_render)

    def raw_render(self):
        vertices = self.vertices
        normals = self.normals
        texure = self.texture

        color = self.color
        if color != None:
            glColor(*color)

        for face in self.faces:
            glBegin(GL_TRIANGLE_FAN)

            # this is very hacky normal calculation (if none given)!
            if face[0][1] == None:
                vv = [ucgf.Vector(*vertices[i[0] - 1]) for i in face]
                ab = vv[1] - vv[0]
                ac = vv[2] - vv[0]
                n = ab.cross(ac)
                n.normalize()

                glNormal(*n)

            # actual rendering of the vertices
            for vert_i, text_i, norm_i in face:
                vertex = vertices[vert_i - 1]

                if norm_i:
                    glNormal(*normals[norm_i - 1])
                
                # TODO: texture coordinates

                glVertex(vertex)

            glEnd()

    def render(self):
        glCallList(self.gl_list)

    def vect_faces(self):
        vertices = self.vertices
        faces = self.faces

        return (tuple(ucgf.Vector(vertices[i-1]) for i, _, _ in f)
                for f in faces)

    def graph(self):
        graph = [GraphNode(vertex) for vertex in self.vertices]

        for face in self.faces:
            l = len(face)
            for index, (vert_i, _, _) in enumerate(face):
                for diff in 1, -1:
                    neighbor_i = face[(index+diff)%l][0]
                    graph[vert_i-1].neighbors.add(graph[neighbor_i-1])

        return graph

    def smooth(self, alpha, depth=1):
        for _ in range(depth):
            print _

            vertices = []

            for node in self.graph():
                neighbors = node.neighbors

                vector = ucgf.Vector(node.vertex)

                balance = ucgf.Vector(0, 0, 0)

                for neighbor in neighbors:
                    balance += ucgf.Vector(neighbor.vertex)

                if len(neighbors) > 0:
                    balance *= 1.0 / len(neighbors)
                else:
                    print "PANIK"

                new_vector = alpha * vector + (1 - alpha) * balance

                #print new_vector.data

                vertices.append(new_vector.data)

            self.vertices = vertices

def main(argv):
    obj = ObjObject(argv[0])
    obj.smooth(0.3, 30)
    ucgf.show_scene([obj])

if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))

