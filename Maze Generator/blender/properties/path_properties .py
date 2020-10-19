"""
This module stores the properties related to the path of the maze and its representation
"""


import bpy.ops
from bpy.types import PropertyGroup, Scene
from bpy.props import (
    IntProperty,
    BoolProperty,
    EnumProperty,
    FloatProperty,
    PointerProperty,
    StringProperty,
    IntVectorProperty,
)


class PathPropertyGroup(PropertyGroup):
    use_random: BoolProperty(
        name="Random Path",
        default=True,
        description="Check this to ensure the path is chosen randomly"
    )

    force_outside: BoolProperty(
        name="Force Outside Path",
        description="Force the maze solution to start and end on the outside of the maze",
        default=False,
    )

    force_start: IntVectorProperty(
        name="Start Maze Here",
        size=2,
    )

    force_end: IntVectorProperty(
        name="End Maze Here",
        size=2,
    )
