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
import obj_parser

def face_surface(face):
    if len(face) != 3:
        raise NotImplementedError("Only triangles allowed")

    a = (face[1] - face[0]).size()
    b = (face[2] - face[0]).size()
    c = (face[1] - face[2]).size()

    s = (a + b + c) / 2.0

    return (s * (s - a) * (s - b) * (s - c)) ** 0.5

def surface(mesh):
    return sum(face_surface(face) for face in mesh.vect_faces())

def volume(mesh):
    return 1.0 / 6 * sum(a * b.cross(c) for a, b, c in mesh.vect_faces())

def main(argv):
    actions = {
            'surface': surface,
            'volume': volume,
            }

    if len(argv) < 1:
        print "Please specify an .obj file"
        return 1

    obj = obj_parser.ObjObject(argv[0])

    for action, fun in actions.items():
        print "%s: %s" % (action, fun(obj))

if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))

