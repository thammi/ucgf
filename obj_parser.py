#!/usr/bin/env python

from warnings import warn

from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

import ucgf

def face_item(l):
    raw = [int(i) if i else None for i in l.split('/')]
    return tuple(raw + [None] * (3 - len(raw)))

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

        # TODO: support other primitives
        for face in self.faces:
            glBegin(GL_TRIANGLE_FAN)

            for vert_i, text_i, norm_i in face:
                vertex = vertices[vert_i - 1]

                if norm_i:
                    glNormal(*normals[norm_i - 1])
                #else:
                    #ab = vertex[1] - polygon[0]
                    #ac = polygon[2] - polygon[0]
                    #n = ab.cross(ac)
                    #n.normalize()

                    #glNormal(*n)
                
                # TODO: texture coordinates

                glVertex(vertex)

            glEnd()

    def render(self):
        glCallList(self.gl_list)

def main(argv):
    ucgf.show_scene([ObjObject(argv[0])])

if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))


