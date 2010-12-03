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
import pygame.image
from OpenGL.GL import *
from OpenGL.GLU import *

import ucgf

class Texture:

    def __init__(self):
        self.sphere = ucgf.Sphere(4, color=(1, 1, 1))

    def gl_init(self):
        img = pygame.image.load('gorilla.bmp')
        data = pygame.image.tostring(img, "RGBA", 1)

        self.texture = texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)

        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)

        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, (1, 1, 1, 1))

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.get_width(), img.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, data)

        self.sphere.gl_init()

    def render(self):
        glPushAttrib(GL_ALL_ATTRIB_BITS)

        # TODO

        glPopAttrib()

def main(argv):
    ucgf.show_scene([Texture()])

if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))

