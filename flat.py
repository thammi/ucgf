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

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

import math

import ucgf

import obj_parser

class Pipe:

    def __init__(self, points, handle=ucgf.Sphere(color=None)):
        self.points = points
        self.cur = 0
        self.handle = handle
        self.tab_lock = False

    def gl_init(self):
        self.handle.gl_init()

    def next_point(self, forward=True):
        delta = 1 if forward else -1
        self.cur = (self.cur + delta) % len(self.points)

    def pipe_points(self):
        raise NotImplementedError()

    def update(self, runtime, keys):
        if K_TAB in keys:
            if not self.tab_lock:
                self.next_point(K_LSHIFT not in keys)
                print self.cur

            self.tab_lock = True
        else:
            self.tab_lock = False

        moves = {
                K_l: (1, 0),
                K_h: (-1, 0),
                K_k: (0, 1),
                K_j: (0, -1),
                }

        for key, move in moves.items():
            if key in keys:
                self.points[self.cur] += ucgf.Vector(move) * runtime

    def render(self):
        handle = self.handle
        cur = self.cur
        points = self.points

        # drawing the handles for the pipe
        factor = 0.2
        for index, point in enumerate(points):
            glPushMatrix()

            if index == cur: 
                glColor(1, 0, 0, 1)
            else:
                glColor(0.5, 0.2, 0.2, 1)

            glTranslate(point[0], point[1], 0)
            glScale(factor, factor, factor)
            handle.render()

            glPopMatrix()

        # turning the light off for the lines
        glDisable(GL_LIGHTING)

        # connecting the handles
        glLineWidth(2)
        glColor(0.2, 0.2, 0.2, 1)
        glBegin(GL_LINE_STRIP)
        for point in points:
            glVertex(point)
        glEnd()

        steps = list(self.pipe_points(100))

        def bend(index):
            if index < 1 or index >= len(steps) - 1:
                return 0

            a, p, b = steps[index-1:index+2]
            angle = math.atan2(*(a-p)) - math.atan2(*(b-p))
            return max(0, min(1, (1 - abs((angle % math.pi * 2)  / math.pi - 1)) ** 0.3))

        # drawing the actual pipe
        glLineWidth(4)
        glColor(0, 0, 1, 1)
        glBegin(GL_LINE_STRIP)
        for index, point in enumerate(steps):
            color = bend(index)
            glColor(0, color, 1 - color, 1)
            glVertex(point)
        glEnd()

        # turning the light on again
        glEnable(GL_LIGHTING)

class BezierPipe(Pipe):

    def pipe_points(self, steps):
        points = self.points
        l = len(points)
        n = l - 1

        def b(i, n, t):
            if n == 0 and i == 0:
                return 1
            elif i < 0 or i > n:
                return 0
            else:
                return (1-t) * b(i, n-1, t) + t * b(i - 1, n - 1, t)

        for t in range(steps):
            i = float(t) / (steps - 1)
            yield sum((b(j, n, i)*points[j] for j in range(l)), ucgf.Vector([0, 0]))

class Lagrange(Pipe):

    def pipe_points(self, steps):
        points = self.points
        l = len(points)
        u = range(l)

        def L(i, t):
            factors = ((t-u[k]) / (u[i]-u[k]) for k in range(l) if k != i)
            return reduce(lambda a, b: a * b, factors)

        for i in range(steps):
            t = float(i) / (steps - 1) * (l - 1)

            parts = (L(index, t) * point for index, point in enumerate(points))
            yield sum(parts, ucgf.Vector(0, 0))

class CoxDeBoor(Pipe):

    def pipe_points(self, steps):
        points = self.points
        l = len(points)
        d = 2
        u = range(l + 1 + d)

        def N(i, g, t):
            if g == 0:
                return 1 if u[i] <= t < u[i+1] else 0

            return (t-u[i])/(u[i+g]-u[i])*N(i, g-1, t) + (u[i+1+g]-t)/(u[i+1+g]-u[i+1])*N(i+1, g-1, t)

        for i in range(steps):
            t = float(i) / (steps - 1) * l
            yield sum((N(j, d, t)*points[j] for j in range(l)), ucgf.Vector([0, 0]))


def read_points(file_name):
    return [ucgf.Vector(map(float, line.split())) for line in open(file_name)]

def main(argv):
    curves = {
            'lagrange': Lagrange,
            'bezier': BezierPipe,
            'cox_de_boor': CoxDeBoor,
            }

    curve = curves[argv[0]]

    points = read_points(argv[1])

    if len(argv) > 2:
        handle = obj_parser.ObjObject(argv[2], color=None)
        handle.center()
        handle.normalize()
    else:
        handle = ucgf.Sphere(color=None)

    #ucgf.show_scene([BezierPipe(points, handle=handle)])
    ucgf.show_scene([curve(points, handle=handle)])

if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))

