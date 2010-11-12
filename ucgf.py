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
import time
import sys

def list_render(render_fun):
    gl_list = glGenLists(1)

    glNewList(gl_list, GL_COMPILE)
    render_fun()
    glEndList()

    return gl_list

class Vector:

    def __init__(self, *data):
        if len(data) == 1:
            self.data = list(data[0])
        else:
            self.data = list(data)

    def len_check(self, size):
        if len(self) != size:
            print len(self)
            raise NotImplementedError

    def __repr__(self):
        return "Vector(%s)" % ', '.join(str(v) for v in self.data)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return self.data.__iter__()
    
    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, value):
        self.data[index] = value

    def __add__(self, other):
        return Vector(a + b for a, b in zip(self, other))

    def __sub__(self, other):
        return Vector(a - b for a, b in zip(self, other))

    def cross(self, other):
        self.len_check(3)

        a = self
        b = other

        return Vector(a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

    def __mul__(self, factor):
        if isinstance(factor, Vector):
            return Vector(v * f for v, f in zip(self, factor))
        else:
            return Vector(v * factor for v in self)

    def __rmul__(self, factor):
        return self.__mul__(factor)
    
    def __imul__(self, factor):
        # TODO: ugly ...
        v = self.__mul__(factor)
        self.data = v.data
        return self

    def size(self):
        self.len_check(3)

        return sum(v*v for v in self.data) ** 0.5
    
    def normalize(self):
        self *= 1. / self.size()

class PolyPackage:

    def __init__(self, color=(1, 0, 1)):
        self.polygons = []
        self.color = color

    def add(self, a, b, c):
        self.polygons.append([a, b, c])

    def gl_init(self):
        self.gl_list = list_render(self.raw_render)

    def raw_render(self):
        glColor(*self.color)

        glBegin(GL_TRIANGLES)

        for polygon in self.polygons:
            ab = polygon[1] - polygon[0]
            ac = polygon[2] - polygon[0]
            n = ab.cross(ac)
            n.normalize()

            glNormal(*n)

            for vector in polygon:
                glVertex(vector)

        glEnd()

    def render(self):
        glCallList(self.gl_list)

    def translate(self, x, y, z):
        delta = (x, y, z)

        for polygon in self.polygons:
            for index in range(3):
                polygon[index] = polygon[index] + delta

    def scale(self, x, y, z):
        factor = Vector(x, y, z)

        for polygon in self.polygons:
            for index in range(3):
                polygon[index] = polygon[index] * factor

class Composite:

    def __init__(self):
        self.objects = []
        self.initialized = False

    def gl_init(self):
        self.initialized = True

        for obj in self.objects:
            if hasattr(obj, 'gl_init'): obj.gl_init()

    def add(self, obj):
        self.objects.append(obj)

        if self.initialized:
            if hasattr(obj, 'gl_init'): obj.gl_init()

    def update(self, runtime, keys):
        for obj in self.objects:
            if hasattr(obj, 'update'): obj.update(runtime, keys)

    def render(self):
        for obj in self.objects:
            if hasattr(obj, 'render'): obj.render()

class Switch:

    def __init__(self, key, value=True):
        self.key = key
        self.value = value
        self.is_down = False

    def update(self, runtime, keys):
        if self.is_down:
            if self.key not in keys:
                self.is_down = False
        else:
            if self.key in keys:
                self.value = not self.value
                self.is_down = True

class Slider:

    def __init__(self, keys, end, start=0, step=1, value=None, rotate=False):
        self.keys = keys
        self.start = start
        self.end = end
        self.value = start if value == None else value
        self.step = step
        self.rotate = rotate

    def change(self, diff):
        value = self.value

        value += diff

        if self.rotate:
            value %= self.end
        else:
            if value < self.start:
                value = self.start
            elif value >= self.end:
                value = self.end

        self.value = value

    def update(self, runtime, keys):
        up, down = self.keys

        if up in keys:
            self.change(runtime * self.step)

        if down in keys:
            self.change(runtime * -self.step)

class PropFarm:

    def __init__(self):
        self.props = {}

    def add(self, name, prop):
        self.props[name] = prop

    def __getitem__(self, name):
        return self.props[name].value

    def update(self, runtime, keys):
        for prop in self.props.itervalues():
            prop.update(runtime, keys)

class Scene:

    def __init__(self, size=(800,600)):
        self.objects = []

        pygame.display.init()
        pygame.display.set_caption("Uber Cool Graphics Framework")

        self.init_cam(size)
        self.init_light()

    def init_cam(self, (width, height)):
        self.ratio = float(width) / height

        #pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES, 4)
        pygame.display.set_mode((width, height), OPENGL | DOUBLEBUF)
        glEnable(GL_MULTISAMPLE)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        #glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glShadeModel(GL_SMOOTH)

        glEnable(GL_NORMALIZE)

        #glEnable(GL_BLEND)
        #glEnable(GL_ALPHA_TEST)
        #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glClearColor(0.23, 0.23, 0.23, 0)


    def init_light(self):
        glEnable(GL_COLOR_MATERIAL)
        # glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glMaterial(GL_FRONT_AND_BACK, GL_SHININESS, 128);
        glMaterial(GL_FRONT_AND_BACK, GL_SPECULAR, (1, 1, 1))
        glMaterial(GL_FRONT_AND_BACK, GL_DIFFUSE, (1, 1, 1))
        glMaterial(GL_FRONT_AND_BACK, GL_AMBIENT, (0, 0, 0))

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLight(GL_LIGHT0, GL_AMBIENT, (0, 0, 0))
        # glLight(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1))
        # glLight(GL_LIGHT0, GL_SPECULAR, (1, 1, 1))
        glLight(GL_LIGHT0, GL_POSITION, (10, 10, 10))
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0, 0, 0, 0))

    def view_init(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, self.ratio, 0.1, 1000)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def add(self, obj):
        self.objects.append(obj)
        
        if hasattr(obj, 'gl_init'): obj.gl_init()

    def loop(self):
        last = time.time()
        keys = set()

        while True:
            events = pygame.event.get()

            for event in events:
                if event.type == QUIT:
                    return
                elif event.type == KEYDOWN:
                    keys.add(event.key)
                elif event.type == KEYUP:
                    keys.discard(event.key)
            
            now = time.time()
            time_diff = now - last

            for obj in self.objects:
                if hasattr(obj, 'update'): obj.update(time_diff, keys)

            self.view_init()

            for obj in self.objects:
                if hasattr(obj, 'render'): obj.render()

            pygame.display.flip()

            last = now
            time.sleep(0.005)

class Showcase(Composite):

    def __init__(self):
        Composite.__init__(self)

        self.props = props = PropFarm()
        props.add('rotate', Slider((K_LEFT, K_RIGHT), end=360, step=60, rotate=True))
        props.add('angle', Slider((K_UP, K_DOWN), end=360, value=30, step=60, rotate=True))
        props.add('move_x', Slider((K_a, K_d), value=0, start=-40, end=400, step=4))
        props.add('move_y', Slider((K_q, K_e), value=0, start=-40, end=40, step=4))
        props.add('move_z', Slider((K_s, K_w), value=10, start=5, end=100, step=8))

        self.add(props)

    def update(self, runtime, keys):
        if K_ESCAPE in keys:
            sys.exit(0)

        Composite.update(self, runtime, keys)

    def render(self):
        props = self.props

        glPushMatrix()

        glTranslate(props['move_x'], props['move_y'], -props['move_z'])
        glRotate(props['angle'], 1, 0, 0)
        glRotate(props['rotate'], 0, 1, 0)

        Composite.render(self)

        glPopMatrix()

class Cube(PolyPackage):

    def __init__(self, color=(1, 0, 1)):
        PolyPackage.__init__(self, color)

        # concept borrowed from twobit

        s = (-0.5, 0.5)
        v = [Vector(x, y, z) for x in s for y in s for z in s]
        p = [
                (0, 1, 3, 2),
                (6, 7, 5, 4),
                (4, 5, 1, 0),
                (2, 3, 7, 6),
                (5, 7, 3, 1),
                (0, 2, 6, 4),
            ]

        for p in p:
            a, b, c, d = (v[i] for i in p)
            self.add(a, b, c)
            self.add(c, d, a)

        # /twobit

class Benchmarker:

    BENCH_LENGTH = 15.0

    def __init__(self):
        self.bench_start = None

    def update(self, runtime, keys):
        if self.bench_start:
            if self.bench_start + self.BENCH_LENGTH > time.time():
                self.frames += 1
            else:
                print "Running at %f per second" % (self.frames / self.BENCH_LENGTH)
                self.bench_start = None
        else:
            if K_m in keys:
                print "Starting benchmark ..."
                self.bench_start = time.time()
                self.frames = 1

def show_scene(objects):
    s = Scene()
    c = Showcase()

    for obj in objects:
        c.add(obj)

    s.add(c)
    s.add(Benchmarker())
    s.loop()

def main(argv):
    cube = Cube()
    show_scene([cube])

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

