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
from maze_generator.blender.generation.main import generate_maze


class PathPropertyGroup(bpy.types.PropertyGroup):
    force_outside: BoolProperty(
        name="Force Outside Path",
        update=generate_maze,
        default=True,
    )
    solution: EnumProperty(
        name="Solution",
        default="Longest",
        items=(
            ("Longest",) * 3,
            ("Random",) * 3,
            ("Custom",) * 3,
        ),
        update=generate_maze,
    )
    start: IntVectorProperty(
        size=2,
        min=0,
        update=generate_maze,
        subtype="XYZ",
    )
    end: IntVectorProperty(
        size=2,
        min=0,
        update=generate_maze,
        subtype="XYZ",
    )
    last_start_cell: IntVectorProperty(
        name="Last Start Cell",
        description="This hidden property will keep the last start cell in memory to avoid flickering when the solving algorithm checks the longest path",
        min=0,
    )
    use_random: BoolProperty(
        name="Random Path", default=True, description="Check this to ensure the path is chosen randomly"
    )
