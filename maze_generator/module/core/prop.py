import bpy

from bpy.props import (
    IntProperty,
    BoolProperty,
    EnumProperty,
    FloatProperty,
    PointerProperty,
    StringProperty,
    IntVectorProperty,
)
from maze_generator.blender.properties.updates import generate_maze


class CorePropertyGroup(bpy.types.PropertyGroup):
    """
    Property group storing Core Parameters
    """

    auto_update: BoolProperty(
        name="Auto Update",
        default=True,
        description="Generate a new maze each time a parameter is modified. This will hurt performance when generating big mazes",
        update=lambda self, context: generate_maze(self, context) if self.auto_update else None,
    )

    auto_overwrite: BoolProperty(
        name="Auto Overwrite",
        description="Caution : Enabling this WILL overwrite the materials, modifiers and drivers",
        default=False,
        update=lambda self, context: generate_maze(self, context) if self.auto_overwrite else None,
    )
