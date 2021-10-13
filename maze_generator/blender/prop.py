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
from maze_generator.blender.generation.prop import GenerationPropertyGroup
from maze_generator.blender.shading.prop import DisplayPropertyGroup
from maze_generator.blender.shading.texture.prop import TexturesPropertyGroup
from maze_generator.blender.interaction.prop import InteractionPropertyGroup
from maze_generator.blender.object.prop import ObjectsPropertyGroup
from maze_generator.blender.object.walls.viewport import update_wall_visibility
from maze_generator.blender.collection.prop import CollectionsPropertyGroup
from maze_generator.blender.modifier.prop import ModifierNamesPropertyGroup
from maze_generator.blender.mesh.prop import MeshesPropertyGroup

from maze_generator.blender.generation.main import generate_maze

from maze_generator.maze.algorithm.prop import AlgorithmPropertyGroup
from maze_generator.maze.space_representation.prop import SpaceRepPropertyGroup
from maze_generator.maze.cell.prop import CellPropertyGroup
from maze_generator.maze.pathfinding.prop import PathPropertyGroup

from maze_generator.maze.algorithm.algorithms import is_algo_weaved

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

    generation: PointerProperty(type=GenerationPropertyGroup)

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
