from . import auto_load
import bpy
from bpy.types import Panel, Menu, Operator, PropertyGroup
from bpy.props import IntProperty, PointerProperty

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


class MGProperties(PropertyGroup):
    test_property: IntProperty(
        name='Test Property',
        description='This is a test property',
        default=5,
        min=0,
        max=10
    )


bl_info = {
    "name": "Maze Generator",
    "author": "NH",
    "description": "",
    "blender": (2, 80, 0),
    "version":  (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Generic"
}

auto_load.init()


def register():
    auto_load.register()
    bpy.types.Scene.mg_props = PointerProperty(type=MGProperties)


def unregister():
    auto_load.unregister()
    del bpy.types.Scene.mg_props
