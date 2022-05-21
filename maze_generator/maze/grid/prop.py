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


def tweak_weave(self, context: bpy.types.Context) -> None:
    self["weave_toggle"] = self.maze.weave > 0
    generate_maze(self, context)


def update_prop(self, value, prop_name):
    if hasattr(self, prop_name):
        setattr(self, prop_name, value)


def toggle_weave(self, context) -> None:
    if self.weave_toggle:
        if self.weave == 0:
            self.weave = 50
    else:
        self.weave = 0


class GridPropertyGroup(bpy.types.PropertyGroup):
    """
    Stores the grid properties
    """

    rows_or_radius: IntProperty(
        name="Rows | Radius",
        description="Choose the size along the Y axis or the radius if using polar coordinates",
        default=10,
        min=2,
        soft_max=100,
        update=generate_maze,
    )

    rows_or_radius_gizmo: FloatProperty(
        name="Rows",
        description="Choose the size along the X axis",
        default=10,
        min=2,
        soft_max=100,
        get=lambda self: self.rows_or_radius / 2,
        set=lambda self, value: update_prop(self, value * 2, "rows_or_radius"),
    )
    random_cells_geomery: FloatProperty(
        name="Random Cells",
        min=0,
        soft_max=1,
        update=generate_maze,
    )
    columns: IntProperty(
        name="Columns",
        description="Choose the size along the X axis",
        default=10,
        min=2,
        soft_max=100,
        update=generate_maze,
    )

    columns_gizmo: FloatProperty(
        name="Columns",
        description="Choose the size along the X axis",
        default=10,
        min=2,
        soft_max=100,
        get=lambda self: self.columns / 2,
        set=lambda self, value: update_prop(self, value * 2, "columns"),
    )

    levels: IntProperty(
        name="Maze Levels",
        description="Choose the size along the Z axis",
        default=1,
        min=1,
        soft_max=5,
        update=generate_maze,
    )

    polar_branch: FloatProperty(
        name="Branch polar grid",
        description="This parameter drives how much the polar grid branches",
        default=1,
        min=0.3,
        soft_max=3,
        update=generate_maze,
    )

    weave: IntProperty(
        name="Weave Maze",
        description="Tweak this value to weave the maze. Not all algorithms allow it",
        default=0,
        min=0,
        max=100,
        subtype="PERCENTAGE",
        update=tweak_weave,
    )

    weave_toggle: BoolProperty(
        name="Weave Maze",
        description="Toggle this value to weave the maze. Not all algorithms allow it",
        default=False,
        update=toggle_weave,
    )
