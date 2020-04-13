from bpy.types import PropertyGroup, Scene
from bpy.props import IntProperty, BoolProperty, EnumProperty, FloatProperty, PointerProperty, FloatVectorProperty, IntVectorProperty
import bpy.ops
from . maze_logic . algorithm_manager import generate_algo_enum, DEFAULT_ALGO
from . visual . cell_type_manager import generate_cell_type_enum, DEFAULT_CELL_TYPE
from . visual . cell_visual import generate_cell_visual_enum, DEFAULT_CELL_VISUAL_TYPE
from Scripts.visual.maze_visual import MazeVisual, MaterialManager
from . visual . space_rep_manager import generate_space_rep_enum, REP_REGULAR
from random import random


def generate_maze(self, context):
    if self.maze_weave and self.cell_thickness == 0:
        self['cell_thickness'] = -0.1
    if self.auto_update and context.mode == "OBJECT":
        bpy.ops.maze.generate()


def update_paint(self, context):
    MaterialManager.set_materials()


def click_randomize_color_button(self, value):
    self.seed_color = random() * 100000
    MaterialManager.set_materials()


def update_modifiers(self, context):
    MazeVisual.generate_modifiers()
    MazeVisual.generate_drivers()


def update_cell_type(self, context):
    reset_enum = True
    for ind, _, _ in generate_space_rep_enum(self, context):
        if self.maze_space_dimension == ind:
            reset_enum = False
            break
    if reset_enum:
        print('Do not worry about these warnings.')
        self['maze_space_dimension'] = REP_REGULAR
    generate_maze(self, context)


def toggle_maze_weave(self, context):
    if self.maze_weave_toggle:
        if self.maze_weave == 0:
            self.maze_weave = 50
    else:
        self.maze_weave = 0


def tweak_maze_weave(self, context):
    self['maze_weave_toggle'] = self.maze_weave > 0
    generate_maze(self, context)


class MGProperties(PropertyGroup):
    auto_update: BoolProperty(
        name='Auto Update',
        default=True,
        description='Generate a new maze each time a parameter is modified. This will hurt performance when generating big mazes',
        update=lambda self, context: generate_maze(self, context) if self.auto_update else None
    )

    auto_overwrite: BoolProperty(
        name="Auto Overwrite",
        description="Caution : Enabling this WILL overwrite the materials, modifiers and drivers",
        default=False,
        update=lambda self, context: generate_maze(self, context) if self.auto_overwrite else None
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

    cell_use_smooth: BoolProperty(
        name='Smooth Shade Cells',
        description='Enforce smooth shading everytime the maze is generated',
        default=False,
        update=lambda self, context: MazeVisual.update_cell_smooth()
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
        update=generate_maze
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
        update=generate_maze
    )

    maze_columns: IntProperty(
        name="Columns",
        description="Choose the size along the X axis",
        default=10,
        min=2,
        soft_max=100,
        update=generate_maze
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

    steps: IntProperty(
        name="Steps",
        description="Set the number of steps at which to stop the algorithm (0 = unlimited)",
        default=0,
        min=0,
        soft_max=10000,
        update=generate_maze
    )

    braid_dead_ends: IntProperty(
        name="Braid Dead Ends",
        description="This percentage of dead-ends will be connected to one of their neighbors",
        default=0,
        min=0,
        max=100,
        subtype='PERCENTAGE',
        update=generate_maze
    )

    sparse_dead_ends: IntProperty(
        name="Sparse Maze",
        description="Choose how many dead ends will be culled subsequently to make a sparser maze",
        default=0,
        min=0,
        max=100,
        subtype='PERCENTAGE',
        update=generate_maze
    )

    wall_hide: BoolProperty(
        name='Wall Hide',
        description="Auto-hide the wall if the cells are inset",
        default=False,
    )

    seed_color: IntProperty(
        name="Color Seed",
        description="Configure the wall default width",
    )

    seed_color_button: BoolProperty(
        name="Color Seed",
        description="Change the seed of the color display",
        default=False,
        set=click_randomize_color_button
    )

    show_only_longest_path: BoolProperty(
        name="Longest Path",
        description="Toggle this property to show only the longest path",
        default=False,
        update=update_paint
    )

    value_shift: FloatProperty(
        name="Color Shift",
        description="Tweak the color value shift of the cells",
        default=0,
        soft_min=-1,
        soft_max=1,
    )

    paint_style: EnumProperty(
        name="Paint Style",
        description="Choose how to paint the cells",
        items=generate_cell_visual_enum(),
        default=DEFAULT_CELL_VISUAL_TYPE,
        update=update_paint
    )

    generation_time: IntProperty(
        name="Generation Time",
    )

    dead_ends: IntProperty(
        name="Dead Ends",
    )

    maze_weave: IntProperty(
        name='Weave Maze',
        description='Tweak this value to weave the maze. Not all algorithms allow it',
        default=0,
        min=0,
        max=100,
        subtype='PERCENTAGE',
        update=tweak_maze_weave
    )

    maze_weave_toggle: BoolProperty(
        name='Weave Maze',
        description='Toggle this value to weave the maze. Not all algorithms allow it',
        default=False,
        update=toggle_maze_weave
    )

    maze_space_dimension: EnumProperty(
        name='Space representation',
        description='Choose if and how to fold the maze in 3D dimensions',
        items=generate_space_rep_enum,
        update=generate_maze
    )

    maze_last_start_cell: IntVectorProperty(
        name='Last Start Cell',
        description='This hidden property will keep the last start cell in memory to avoid flickering when the solving algorithm checks the longest path',
        min=0
    )

    info_show_help: BoolProperty(
        name='Show Help',
        description='When toggled ON, this will add more precisions to each field in the panels',
        default=False
    )

    def register():
        Scene.mg_props = PointerProperty(type=MGProperties)

    def unregister():
        del Scene.mg_props
