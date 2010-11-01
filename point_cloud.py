from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

import ucgf

class PointCloud:

    def __init__(self, vectors=[]):
        self.vectors = vectors

        self.props = props = ucgf.PropFarm()
        props.add('list_mode', ucgf.Switch(K_d))
        props.add('point_size', ucgf.Slider((K_PERIOD, K_COMMA), start=1, end=10, step=4))

    def gl_init(self):
        self.gl_list = gl_list = glGenLists(1)
        glNewList(gl_list, GL_COMPILE)
        self.raw_render()
        glEndList()

    def raw_render(self):
        glColor(0, 1, 0)
        glBegin(GL_POINTS)
        for point, normal in self.vectors:
            glNormal(*normal)
            glVertex(point)
        glEnd()

    def update(self, runtime, keys):
        self.props.update(runtime, keys)

    def render(self):
        glPointSize(self.props['point_size'])

        if self.props['list_mode']:
            glCallList(self.gl_list)
        else:
            self.raw_render()

def load_cloud(file_name):
    inp = open(file_name)
    data = [[],[]]

    for line in inp:
        cols = line.split()
        data[len(cols[0])-1].append(tuple(float(v) for v in cols[1:]))

    vectors = zip(*data)

    return PointCloud(vectors)

def main(argv):
    ucgf.show_scene([load_cloud(argv[0])])

if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))

