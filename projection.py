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
        self.cube = ucgf.Cube()
        self.props = props = ucgf.PropFarm()
        props.add('front_face', ucgf.Switch(K_b))

    def gl_init(self):
        glEnable(GL_CULL_FACE)

    def update(self, runtime, keys):
        self.props.update(runtime, keys)

    def render(self):
        props = self.props
        front_face = props['front_face']

        glFrontFace(GL_CCW if front_face else GL_CW)

        cube = self.cube
        cube.invert_normals = not front_face
        cube.raw_render()

        glFrontFace(GL_CCW)


def main(argv):
    ucgf.show_scene([Projection()])

if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))

