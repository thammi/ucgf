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

print "ROBOTS ARE TAKING OVER"

class Robot:

    def __init__(self):
        key_mapping = [
                    (K_t, K_g),
                    (K_h, K_y),
                    (K_j, K_u),
                    (K_i, K_k),
                    (K_o, K_l),
                ]

        self.values = [ucgf.Slider(keys, 360, value=30, step=30, rotate=True)
                for keys in key_mapping[:-1]]

        # add the claws
        self.values.append(ucgf.Slider(key_mapping[-1], 0.75, 0))

        # fix some values
        self.values[0].value = 0
        self.values[-2].value = 0

        stand = ucgf.Tube(128)
        stand.translate(0, 0.5, 0)
        stand.scale(3, 1, 3)

        podium = ucgf.Cube(color=(0.7, 0.7, 0.7))
        podium.scale(15, 0.1, 15)

        podium.assimilate(stand)
        podium.translate(0, -1, 0)

        limb = ucgf.Cube(color=(1, 0, 0))
        limb.scale(1, 7, 1)
        limb.translate(0, 3, 0)

        head = ucgf.Cube(color=(0.3, 0.3, 0.7))
        head.scale(3, 0.4, 1.5)

        claw = ucgf.Cube(color=(0.5, 0.5, 0.8))
        claw.scale(1, 1.5, 0.5)
        claw.translate(0, 0.75, 0.3)

        self.parts = {
                'podium': podium,
                'limb': limb,
                'head': head,
                'claw': claw,
                }

    def gl_init(self):
        for obj in self.parts.itervalues():
            obj.gl_init()

    def update(self, runtime, keys):
        for obj in self.values:
            obj.update(runtime, keys)

    def render(self):
        parts = self.parts
        values = self.values

        glPushMatrix()

        glScale(0.2, 0.2, 0.2)
        glTranslate(0, -2, 0)

        parts['podium'].render()

        glRotate(self.values[0].value, 0, 1, 0)

        for slider in values[1:-2]:
            glRotate(slider.value, -1, 0, 0)
            parts['limb'].render()
            glTranslate(0, 6.5, 0)

        glRotate(values[-2].value, 0, 1, 0)
        parts['head'].render()

        for angle in (90, -90):
            glPushMatrix()

            glRotate(angle, 0, 1, 0)
            glTranslate(0, 0, values[-1].value)
            parts['claw'].render()

            glPopMatrix()

        glPopMatrix()

def main(argv):
    ucgf.show_scene([Robot()])

if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))

