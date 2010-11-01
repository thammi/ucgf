import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import time
import sys

from vec import vec

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
        props.add('move_x', Slider((K_d, K_a), value=0, start=-40, end=400, step=4))
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

class Cube:

    def __init__(self):
        self.gl_list = gl_list = glGenLists(1)
        glNewList(gl_list, GL_COMPILE)
        self.raw_render()
        glEndList()

    def raw_render(self):
        # create a cube
        s = (-1, 1)
        v = [vec(x, y, z) for x in s for y in s for z in s]
        p = [
                (0, 1, 3, 2),
                (6, 7, 5, 4),
                (4, 5, 1, 0),
                (2, 3, 7, 6),
                (5, 7, 3, 1),
                (0, 2, 6, 4),
            ]

        for p in p:
            glColor(0, 0, 1)
            glBegin(GL_TRIANGLE_FAN)
            a, b, c = (v[i] for i in p[:3])
            ab = b - a
            ac = c - a
            n = ab.cross(ac).normalize()
            glNormal(*n)
            for i in p: glVertex(v[i])
            glEnd()

    def render(self):
        glCallList(self.gl_list)

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
    show_scene([Cube()])

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

