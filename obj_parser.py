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
from random import Random

from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

import ucgf
from ucgf import Vector

def in_triangle(point, triangle):
    a, b, c = triangle
    p = point

    v0 = c - a
    v1 = b - a
    v2 = p - a

    dot00 = v0 * v0
    dot01 = v0 * v1
    dot02 = v0 * v2
    dot11 = v1 * v1
    dot12 = v1 * v2

    denom = (dot00 * dot11 - dot01 * dot01)

    if denom:
        u = (dot11 * dot02 - dot01 * dot12) / denom
        v = (dot00 * dot12 - dot01 * dot02) / denom

        e = p - (u * v0 + v * v1)

        diff = sum(e)

        return u > 0 and v > 0 and u + v < 1 and diff < 10**-10
    else:
        return False

def face_item(l):
    raw = [int(i) if i else None for i in l.split('/')]
    return tuple(raw + [None] * (3 - len(raw)))

def face_str(face):
    if any(face[1:]):
        return '/'.join(str(i) if i else "" for i in face)
    else:
        return str(face[0])

class GraphNode:

    def __init__(self, vertex):
        self.vertex = vertex

        self.faces = set()
        self.neighbors = set()

class ObjObject:

    def __init__(self, file_name, color=(1, 0, 1), color_fun=False):
        self.color = color
        self.color_fun = color_fun

        self.vertices = vertices = []
        self.normals = normals = []
        self.texture = texture = []
        self.faces = faces = []
        self.strips = strips = []
        
        inp = open(file_name)

        actions = {
                'v': lambda l: vertices.append(Vector(float(i) for i in l)),
                'vn': lambda l: normals.append(Vector(float(i) for i in l)),
                'vt': lambda l: texture.append(tuple(float(i) for i in l)),
                'f': lambda l: faces.append([face_item(i) for i in l]),
                }

        for line in inp:
            if line[0] != '#' and not line.isspace():
                args = line.split()

                cmd = args[0]

                if cmd in actions:
                    actions[args[0]](args[1:])
                else:
                    warn("Unknown command: " + cmd)

    def save_obj(self, file_name):
        parts = [
                ('v', self.vertices, str),
                ('vt', self.texture, str),
                ('vn', self.normals, str),
                ('f', self.faces, face_str),
                ]

        out = open(file_name, "w")

        for name, items, str_fun in parts:
            for item in items:
                out.write(name)

                for sub in item:
                    out.write(" ")
                    out.write(str_fun(sub))

                out.write("\n")

        out.close()

    def gl_init(self):
        self.gl_list = ucgf.list_render(self.raw_render)

    def raw_render(self):
        color = self.color
        if color != None:
            glColor(*color)

        self.render_polygons(GL_TRIANGLE_FAN, self.faces)
        self.render_polygons(GL_TRIANGLE_STRIP, self.strips)

    def render_polygons(self, mode, faces):
        vertices = self.vertices
        normals = self.normals
        texure = self.texture
        color_fun = self.color_fun

        if color_fun:
            r = Random()

        for face in faces:
            glBegin(mode)

            if color_fun:
                glColor(*([r.randint(10, 50) / 50.0 for i in range(3)] + [255]))

            # this is very hacky normal calculation (if none given)!
            if face[0][2] == None:
                vv = [vertices[i[0] - 1] for i in face]
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

        return (tuple(vertices[i-1] for i, _, _ in f) for f in faces)

    def graph(self):
        graph = [GraphNode(vertex) for vertex in self.vertices]

        for face in self.faces:
            l = len(face)
            for index, (vert_i, _, _) in enumerate(face):
                for diff in 1, -1:
                    neighbor_i = face[(index+diff)%l][0]
                    graph[vert_i-1].neighbors.add(graph[neighbor_i-1])

        return graph

    def expand_strip(self, face, node):
        raise NotImplementedError()

    def strip_triangles(self, samples=1):
        faces = self.faces
        strips = self.strips
        rand = Random()

        while faces:
            possible_strips = []

            for i in range(samples):
                face = rand.randint(0, len(faces))
                node = rand.randint(0, len(faces[face]))

                strip, consumed = expand_strip(face, node)

                possible_strips.append((strip, consumed))

            strip, consumed = max(possible_strips, lambda (s, c): len(s))

            for index in consumed:
                del faces[index]

            strips.append(strip)

    def triangulate(self):
        # ear clipping

        vertices = self.vertices
        faces = self.faces

        for face in list(faces):
            l = len(face)

            # TODO: hacky but speedy
            if l == 3:
                continue

            def is_convex(index):
                a = vertices[face[(index-1)%l][0]-1]
                b = vertices[face[(index+1)%l][0]-1]
                p = vertices[face[index][0]-1]

                pa = a - p
                pb = b - p
                ap = p - a

                return pa.cross(pb) * ap.cross(pb) < 0

            # determine convex and convex nodes
            convex = set(node for i, node in enumerate(face) if is_convex(i))

            # just enough iterations to triangulate the face
            for i in range(l-3):
                # get all convex nodes with index
                convex_nodes = [(i, n) for i, n in enumerate(face) if n in convex]

                # test each convex node
                for index, node in reversed(convex_nodes):
                    # find neighbors
                    prev = face[(index-1)%l]
                    foll = face[(index+1)%l]

                    # check for collisions with concave nodes
                    for conc_node in (n for n in face if n not in convex):
                        point = vertices[conc_node[0]-1]
                        triangle = [vertices[n[0]-1] for n in prev, node, foll]

                        if in_triangle(point, triangle):
                            break
                    else:
                        # remove the ear
                        l -= 1
                        del face[index]

                        # add a new triangle
                        faces.append([prev, node, foll])

                        # re-classify previous node
                        if prev not in convex:
                            if is_convex(index-1):
                                convex.add(prev)

                        # re-classify following node
                        if foll not in convex:
                            if is_convex(index):
                                convex.add(prev)

                        # let's have another run
                        break

    def noise(self, sigma):
        rand = Random()
        self.vertices = [Vector(rand.gauss(x, sigma) for x in vertex)
                for vertex in self.vertices]

    def smooth(self, alpha, depth=1):
        for _ in range(depth):
            print _

            vertices = []

            for node in self.graph():
                neighbors = node.neighbors

                balance = Vector(0, 0, 0)

                for neighbor in neighbors:
                    balance += neighbor.vertex

                if len(neighbors) > 0:
                    balance *= 1.0 / len(neighbors)
                else:
                    warn("Vertex without neighbor")

                vertices.append(alpha * node.vertex + (1 - alpha) * balance)

            self.vertices = vertices

    def center(self):
        vertices = self.vertices

        if len(vertices) == 0:
            return

        maxs = list(vertices[0])
        mins = list(vertices[0])

        for vertex in vertices[1:]:
            for axis, part in enumerate(vertex):
                if part < mins[axis]:
                    mins[axis] = part
                if part > maxs[axis]:
                    maxs[axis] = part

        aabb_center = (ucgf.Vector(mins) + ucgf.Vector(maxs)) * 0.5

        self.vertices = [v - aabb_center for v in vertices]

    def normalize(self):
        vertices = self.vertices
        factor = 1. / max(v.size() for v in vertices)
        self.vertices = [v * factor for v in vertices]

def main(argv):
    obj = ObjObject(argv[0], color_fun=True)

    actions = {
            'smooth': lambda a=0.3, n=1: obj.smooth(float(a), int(n)),
            'noise': lambda s=0.01: obj.noise(float(s)),
            'obj': lambda fn='tmp.obj': obj.save_obj(fn),
            'ear': lambda: obj.triangulate(),
            'center': obj.center,
            'normalize': obj.normalize
            }

    for arg in argv[1:]:
        parts = arg.split(":")
        actions[parts[0]](*parts[1:])

    ucgf.show_scene([obj])

if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))

