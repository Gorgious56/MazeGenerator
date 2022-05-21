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

from maze_generator.maze.algorithm.prop import AlgorithmPropertyGroup
from maze_generator.maze.space_representation.prop import SpaceRepPropertyGroup
from maze_generator.maze.cell.prop import CellPropertyGroup
from maze_generator.maze.pathfinding.prop import PathPropertyGroup
from maze_generator.maze.grid.prop import GridPropertyGroup

from maze_generator.maze.algorithm.algorithms import is_algo_weaved


def update_objects_visibility(self, context) -> None:
    update_wall_visibility(self, is_algo_weaved(self))


class MGProperties(PropertyGroup):
    """
    Main properties group to store the add-on properties
    """
    grid = None  # Used to keep reference of the Grid object

    maze: PointerProperty(type=GridPropertyGroup)

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

    wall_hide: BoolProperty(
        name="Wall Hide",
        description="Keep the wall hidden",
        default=False,
        update=update_objects_visibility,
    )

    generation_time: IntProperty(
        name="Generation Time",
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
