"""
All the add-on properties and callbacks are stored here
"""

import bpy.ops
from bpy.types import (
    PropertyGroup,
    Scene,
)
from bpy.props import (
    IntProperty,
    BoolProperty,
    EnumProperty,
    FloatProperty,
    PointerProperty,
    StringProperty,
    IntVectorProperty,
)
from maze_generator.module.algorithm.prop import AlgorithmPropertyGroup
from maze_generator.module.core.prop import CorePropertyGroup
from maze_generator.module.display.prop import DisplayPropertyGroup
from maze_generator.module.interaction.prop import InteractionPropertyGroup

# from .path_properties import PathPropertyGroup
from ..meshes import MeshManager

from ..objects import (
    update_wall_visibility,
    ObjectsPropertyGroup,
)
from ..meshes import MeshesPropertyGroup
from ..collections import CollectionsPropertyGroup
from ..modifiers.manager import ModifierNamesPropertyGroup

from ..shading.textures import TexturesPropertyGroup

from maze_generator.module.algorithm.algorithms import is_algo_weaved

from maze_generator.module.space_representation.prop import SpaceRepPropertyGroup
from maze_generator.module.cell.prop import CellPropertyGroup
from maze_generator.module.pathfinding.prop import PathPropertyGroup
from .updates import generate_maze


def toggle_maze_weave(self, context) -> None:
    if self.maze_weave_toggle:
        if self.maze_weave == 0:
            self.maze_weave = 50
    else:
        self.maze_weave = 0


def update_objects_visibility(self, context) -> None:
    update_wall_visibility(self, is_algo_weaved(self))


def tweak_maze_weave(self, context: bpy.types.Context) -> None:
    self["maze_weave_toggle"] = self.maze_weave > 0
    generate_maze(self, context)


def update_prop(self, value, prop_name):
    if hasattr(self, prop_name):
        setattr(self, prop_name, value)


class MGProperties(PropertyGroup):
    """
    Main properties group to store the add-on properties
    """

    grid = None

    core: PointerProperty(type=CorePropertyGroup)

    collections: PointerProperty(type=CollectionsPropertyGroup)
    objects: PointerProperty(type=ObjectsPropertyGroup)
    meshes: PointerProperty(type=MeshesPropertyGroup)
    textures: PointerProperty(type=TexturesPropertyGroup)

    mod_names: PointerProperty(type=ModifierNamesPropertyGroup)

    cell_props: PointerProperty(type=CellPropertyGroup)
    space_rep_props: PointerProperty(type=SpaceRepPropertyGroup)
    algorithm: PointerProperty(type=AlgorithmPropertyGroup)
    path: PointerProperty(type=PathPropertyGroup)
    interaction: PointerProperty(type=InteractionPropertyGroup)
    display: PointerProperty(type=DisplayPropertyGroup)

    maze_rows_or_radius: IntProperty(
        name="Rows | Radius",
        description="Choose the size along the Y axis or the radius if using polar coordinates",
        default=10,
        min=2,
        soft_max=100,
        update=generate_maze,
    )

    maze_rows_or_radius_gizmo: FloatProperty(
        name="Rows",
        description="Choose the size along the X axis",
        default=10,
        min=2,
        soft_max=100,
        get=lambda self: self.maze_rows_or_radius / 2,
        set=lambda self, value: update_prop(self, value * 2, "maze_rows_or_radius"),
    )

    maze_columns: IntProperty(
        name="Columns",
        description="Choose the size along the X axis",
        default=10,
        min=2,
        soft_max=100,
        update=generate_maze,
    )

    maze_columns_gizmo: FloatProperty(
        name="Columns",
        description="Choose the size along the X axis",
        default=10,
        min=2,
        soft_max=100,
        get=lambda self: self.maze_columns / 2,
        set=lambda self, value: update_prop(self, value * 2, "maze_columns"),
    )

    maze_levels: IntProperty(
        name="Maze Levels",
        description="Choose the size along the Z axis",
        default=1,
        min=1,
        soft_max=5,
        update=generate_maze,
    )

    maze_basement: BoolProperty(name="Equalize Thickness", description="Add a basement to the maze", default=True)

    maze_polar_branch: FloatProperty(
        name="Branch polar grid",
        description="This parameter drives how much the polar grid branches",
        default=1,
        min=0.3,
        soft_max=3,
        update=generate_maze,
    )
    wall_hide: BoolProperty(
        name="Wall Hide",
        description="Keep the wall hidden",
        default=False,
        update=update_objects_visibility,
    )

    generation_time: IntProperty(
        name="Generation Time",
    )

    maze_weave: IntProperty(
        name="Weave Maze",
        description="Tweak this value to weave the maze. Not all algorithms allow it",
        default=0,
        min=0,
        max=100,
        subtype="PERCENTAGE",
        update=tweak_maze_weave,
    )

    maze_weave_toggle: BoolProperty(
        name="Weave Maze",
        description="Toggle this value to weave the maze. Not all algorithms allow it",
        default=False,
        update=toggle_maze_weave,
    )

    info_show_help: BoolProperty(
        name="Show Help",
        description="When toggled ON, this will add more precisions to each field in the panels",
        default=False,
    )

    def register():
        Scene.mg_props = PointerProperty(type=MGProperties)

    def unregister():
        del Scene.mg_props
