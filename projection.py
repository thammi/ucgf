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

from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

import ucgf

class Projection:

    def __init__(self):
        self.cube = ucgf.Cube(color=(0.5, 0.5, 1))
        self.props = props = ucgf.PropFarm()

        self.ball = ball = ucgf.Sphere(3, color=None)
        ball.scale(*[0.2]*3)

        props.add('front_face', ucgf.Switch(K_b))
        props.add('inverse', ucgf.Switch(K_i))

        keys = [
                ('p_x', (K_r, K_f), 0),
                ('p_y', (K_t, K_g), 0),
                ('p_z', (K_y, K_h), -0.5),
                ]

        for name, keys, default in keys:
            props.add(name, ucgf.Slider(keys, start=-2, end=2, value=default, step=-.3))

    def gl_init(self):
        glEnable(GL_CULL_FACE)
        self.ball.gl_init()

    def update(self, runtime, keys):
        self.props.update(runtime, keys)

    def render(self):
        props = self.props
        front_face = props['front_face']

        glFrontFace(GL_CCW if front_face else GL_CW)

        glPushMatrix()

        m = [
            1, 0, 0, props['p_x'],
            0, 1, 0, props['p_y'],
            0, 0, 1, props['p_z'],
            0, 0, 0, 1,
            ]

        if props['inverse']:
            for i in range(3):
                m[3 + (4 * i)] *= -1

        glMultMatrixf(m)

        cube = self.cube
        cube.invert_normals = not front_face
        cube.raw_render()

        glPopMatrix()

        glFrontFace(GL_CCW)

        for index, name in enumerate(['p_x', 'p_y', 'p_z']):
            if props[name]:
                pos = [0, 0, 0]
                pos[index] = 1 / props[name]

                color = [0, 0, 0]
                color[index] = 1

                glColor(*color)

                glPushMatrix()
                glTranslate(*pos)
                self.ball.render()
                glPopMatrix()


def main(argv):
    ucgf.show_scene([Projection()])

if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))

