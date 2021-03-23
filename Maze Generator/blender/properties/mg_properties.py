"""
All the add-on properties and callbacks are stored here
"""

from enum import Enum
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
# from .path_properties import PathPropertyGroup
from ..meshes import (
    generate_cell_visual_enum,
    DEFAULT_CELL_VISUAL_TYPE,
    MeshManager,
)

from ..objects import (
    update_wall_visibility,
    ObjectsPropertyGroup,
)
from ..meshes import MeshesPropertyGroup
from ..collections import CollectionsPropertyGroup
from ..modifiers.manager import ModifierNamesPropertyGroup

from ..shading.objects import manager as material_manager
from ..shading.materials import MaterialsPropertyGroup
from ..shading.textures import TexturesPropertyGroup

from ...maze_logic.algorithms.manager import (
    generate_algo_enum,
    is_algo_weaved,
    DEFAULT_ALGO,
)
from ...maze_logic.cells import (
    generate_cell_type_enum,
    DEFAULT_CELL_TYPE,
    CellType,
)

from ...blender.operators.op_generate_maze import MG_OT_GenerateMaze


class SpaceRepsPropertyGroup(PropertyGroup):
    """
    Stores the different space representations
    """
    regular: StringProperty(
        default='0'
    )
    cylinder: StringProperty(
        default='1'
    )
    moebius: StringProperty(
        default='2'
    )
    torus: StringProperty(
        default='3'
    )
    box: StringProperty(
        default='4'
    )


def generate_space_rep_enum(self, context):
    space_reps = self.space_reps
    ret = [(space_reps.regular, 'Plane', '')]
    if not self.is_cell_type(CellType.POLAR):
        ret.extend((
            (space_reps.cylinder, 'Cylinder', ''),
            (space_reps.moebius, 'Moebius', ''),
            (space_reps.torus, 'Torus', '')))
        # (space_reps.box, 'Box', '')))
    return ret


def generate_maze(self, context) -> None:
    if context.scene.mg_props.auto_update and context.mode == "OBJECT":
        exec(f"bpy.ops.{MG_OT_GenerateMaze.bl_idname}()")


def update_inset(self, context) -> None:
    generate_maze(self, context)


def update_paint(self, context: bpy.types.Context) -> None:
    material_manager.update_links(self)
    if not self.show_longest_path:
        self.objects.cells.modifiers[self.mod_names.mask_longest_path].show_viewport = False


def update_cell_type(self, context: bpy.types.Context) -> None:
    reset_enum = True
    for ind, _, _ in generate_space_rep_enum(self, context):
        if self.maze_space_dimension == ind:
            reset_enum = False
            break
    if reset_enum:
        print('Do not worry about these warnings.')
        self['maze_space_dimension'] = self.space_reps.regular
    generate_maze(self, context)


def toggle_maze_weave(self, context) -> None:
    if self.maze_weave_toggle:
        if self.maze_weave == 0:
            self.maze_weave = 50
    else:
        self.maze_weave = 0


def update_objects_visibility(self, context) -> None:
    update_wall_visibility(self, is_algo_weaved(self))


def tweak_maze_weave(self, context: bpy.types.Context) -> None:
    self['maze_weave_toggle'] = self.maze_weave > 0
    generate_maze(self, context)


def update_prop(self, value, prop_name):
    if hasattr(self, prop_name):
        setattr(self, prop_name, value)


class PathPropertyGroup(PropertyGroup):
    force_outside: BoolProperty(
        name="Force Outside Path",
        update=generate_maze,
        default=True,
    )
    solution: EnumProperty(
        name="Solution",
        default="Longest",
        items=(
            ("Longest",)*3,
            ("Random",)*3,
            ("Custom",)*3,
        ),
        update=generate_maze,
    )
    start: IntVectorProperty(
        size=2,
        min=0,
        update=generate_maze,
        subtype='XYZ',
    )
    end: IntVectorProperty(
        size=2,
        min=0,
        update=generate_maze,
        subtype='XYZ',
    )


class MGProperties(PropertyGroup):
    """
    Main properties group to store the add-on properties
    """
    grid = None

    space_reps: PointerProperty(
        type=SpaceRepsPropertyGroup
    )

    meshes: PointerProperty(
        type=MeshesPropertyGroup
    )

    collections: PointerProperty(
        type=CollectionsPropertyGroup
    )

    objects: PointerProperty(
        type=ObjectsPropertyGroup
    )

    mod_names: PointerProperty(
        type=ModifierNamesPropertyGroup
    )

    materials: PointerProperty(
        type=MaterialsPropertyGroup
    )

    textures: PointerProperty(
        type=TexturesPropertyGroup,
    )

    path: PointerProperty(
        type=PathPropertyGroup,
    )

    show_gizmos: BoolProperty(
        name="Show Gizmos",
        default=True,
        description="Check this to display the interactive gizmos",
    )

    auto_update: BoolProperty(
        name='Auto Update',
        default=True,
        description='Generate a new maze each time a parameter is modified. This will hurt performance when generating big mazes',
        update=lambda self, context: generate_maze(
            self, context) if self.auto_update else None
    )

    auto_overwrite: BoolProperty(
        name="Auto Overwrite",
        description="Caution : Enabling this WILL overwrite the materials, modifiers and drivers",
        default=False,
        update=lambda self, context: generate_maze(
            self, context) if self.auto_overwrite else None
    )

    maze_algorithm: EnumProperty(
        name="Algorithm",
        description="Choose which algorithm will generate the maze",
        items=generate_algo_enum(),
        default=DEFAULT_ALGO,
        update=generate_maze
    )

    cell_type: EnumProperty(
        name="Cell Type",
        description="The shape of the maze's cells",
        items=generate_cell_type_enum(),
        default=DEFAULT_CELL_TYPE,
        update=update_cell_type
    )

    meshes_use_smooth: BoolProperty(
        name='Smooth Shade Meshes',
        description='Enforce smooth shading everytime the maze is generated',
        default=False,
        update=lambda self, context: MeshManager.update_smooth(self)
    )

    cell_decimate: IntProperty(
        name='Cell Decimate',
        description='Set the ratio of faces to decimate.',
        default=0,
        min=0,
        max=100,
        subtype='PERCENTAGE'
    )

    cell_inset: FloatProperty(
        name="Cell Inset",
        description="Tweak the cell's inset",
        default=0,
        soft_max=0.9,
        min=0,
        max=1,
        update=update_inset
    )

    cell_contour: FloatProperty(
        name='Cell Bevel',
        description='Add bevel to the cells',
        default=0,
        min=0,
        soft_max=0.2
    )

    cell_contour_black: BoolProperty(
        name='Cell Contour',
        description='This will add a stylised black contour to the cells',
        default=False
    )

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
        set=lambda self, value: update_prop(
            self, value * 2, "maze_rows_or_radius"),
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
        update=generate_maze
    )

    seed: IntProperty(
        name="Seed",
        description="This seed will be used to randomize the maze",
        default=0,
        min=0,
        update=generate_maze
    )

    maze_bias: FloatProperty(
        name="Bias",
        description="Add a bias to the algorithm in a certain direction",
        default=0,
        soft_min=-1,
        soft_max=1,
        subtype='FACTOR',
        update=generate_maze
    )

    maze_room_size: IntProperty(
        name='Room Size',
        description='tweak this to stop the recursive division when the room size is lower than the number',
        default=5,
        min=2,
        soft_max=200,
        update=generate_maze
    )

    maze_room_size_deviation: IntProperty(
        name='Room Size Deviation',
        description='tweak this to add randomness to the room size property. At a value of 1, the room size will vary between the minimum and the value in the room property',
        default=0,
        min=0,
        soft_max=100,
        subtype='PERCENTAGE',
        update=generate_maze
    )

    maze_basement: BoolProperty(
        name='Equalize Thickness',
        description='Add a basement to the maze',
        default=True
    )

    maze_polar_branch: FloatProperty(
        name='Branch polar grid',
        description='This parameter drives how much the polar grid branches',
        default=1,
        min=0.3,
        soft_max=3,
        update=generate_maze,
    )

    keep_dead_ends: IntProperty(
        name="Braid Dead Ends",
        description="This percentage of dead-ends will be connected to one of their neighbors",
        default=100,
        min=0,
        max=100,
        subtype='PERCENTAGE',
        update=generate_maze,
    )

    sparse_dead_ends: IntProperty(
        name="Sparse Maze",
        description="Choose how many dead ends will be culled subsequently to make a sparser maze",
        default=0,
        min=0,
        max=100,
        subtype='PERCENTAGE',
        update=generate_maze,
    )

    wall_hide: BoolProperty(
        name='Wall Hide',
        description="Keep the wall hidden",
        default=False,
        update=update_objects_visibility,
    )

    seed_color: IntProperty(
        name="Color Seed",
        description="Configure the wall default width",
    )

    show_longest_path: BoolProperty(
        name="Longest Path",
        description="Toggle this property to show the longest path",
        default=False,
        update=update_paint,
    )

    paint_style: EnumProperty(
        name="Paint Style",
        description="Choose how to paint the cells",
        items=generate_cell_visual_enum(),
        default=DEFAULT_CELL_VISUAL_TYPE,
        update=update_paint,
    )

    generation_time: IntProperty(
        name="Generation Time",
    )

    maze_weave: IntProperty(
        name='Weave Maze',
        description='Tweak this value to weave the maze. Not all algorithms allow it',
        default=0,
        min=0,
        max=100,
        subtype='PERCENTAGE',
        update=tweak_maze_weave,
    )

    maze_weave_toggle: BoolProperty(
        name='Weave Maze',
        description='Toggle this value to weave the maze. Not all algorithms allow it',
        default=False,
        update=toggle_maze_weave,
    )

    maze_space_dimension: EnumProperty(
        name='Space representation',
        description='Choose if and how to fold the maze in 3D dimensions',
        items=generate_space_rep_enum,
        update=generate_maze,
    )

    maze_last_start_cell: IntVectorProperty(
        name='Last Start Cell',
        description='This hidden property will keep the last start cell in memory to avoid flickering when the solving algorithm checks the longest path',
        min=0,
    )

    info_show_help: BoolProperty(
        name='Show Help',
        description='When toggled ON, this will add more precisions to each field in the panels',
        default=False,
    )

    def is_cell_type(self, cell_type: Enum) -> bool:
        return self.cell_type == cell_type.value

    def register():
        Scene.mg_props = PointerProperty(type=MGProperties)

    def unregister():
        del Scene.mg_props
