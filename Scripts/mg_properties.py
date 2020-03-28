from bpy.types import PropertyGroup, Scene
from bpy.props import IntProperty, BoolProperty, EnumProperty, FloatProperty, PointerProperty, FloatVectorProperty
import bpy.ops
from . maze_logic . algorithm_manager import generate_algo_enum, DEFAULT_ALGO
from . visual . cell_type_manager import generate_cell_type_enum, DEFAULT_CELL_TYPE
from . visual . cell_visual_manager import generate_cell_visual_enum, DEFAULT_CELL_VISUAL_TYPE
from . visual . maze_visual import MazeVisual
from random import random


def generate_maze(self, context):
    if self.auto_update and context.mode == "OBJECT":
        bpy.ops.maze.generate()


def update_paint(self, context):
    if MazeVisual.Instance:
        MazeVisual.Instance.set_materials()
        MazeVisual.Instance.update_visibility()


def click_randomize_color_button(self, value):
    self.seed_color = random() * 100000
    if MazeVisual.Instance:
        MazeVisual.Instance.set_materials()
        MazeVisual.Instance.paint_cells()


def update_modifiers(self, context):
    if MazeVisual.Instance:
        MazeVisual.Instance.generate_modifiers()
        MazeVisual.Instance.generate_drivers()


def update_cell_smooth(self, context):
    if MazeVisual.Instance:
        MazeVisual.Instance.update_cell_smooth()


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
        update=generate_maze
    )

    auto_overwrite: BoolProperty(
        name="Auto Overwrite",
        description="Caution : Enabling this WILL overwrite any material and modifiers with new ones when generating",
        default=False,
        update=generate_maze
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
        update=generate_maze
    )

    cell_use_smooth: BoolProperty(
        name='Smooth Shade Cells',
        description='Enforce smooth shading everytime the maze is generated',
        default=False,
        update=update_cell_smooth
    )

    cell_subdiv: IntProperty(
        name='Cell Subidivison',
        description='Subidivide the cells. WARNING : Will take a long time to compute on larger mazes.',
        default=0,
        min=0,
        soft_max=3,
        max=6
    )

    rows_or_radius: IntProperty(
        name="Rows | Radius",
        description="Choose the size along the y axis or the radius if using polar coordinates",
        default=5,
        min=2,
        soft_max=100,
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

    wall_height: FloatProperty(
        name="Height",
        description="Configure the wall default height",
        default=0.5,
        soft_min=0,
    )

    wall_width: FloatProperty(
        name="Width",
        description="Configure the wall default width",
        default=0.2,
        min=0,
        soft_max=2,
    )

    wall_color: FloatVectorProperty(
        name='Wall Color',
        description="Change the wall's displayed color",
        subtype='COLOR',
        default=(0, 0, 0),
        min=0,
        max=1,
        update=update_paint
    )

    wall_hide: BoolProperty(
        name='Wall Hide',
        description="Auto-hide the wall if the cells are inset",
        default=True,
    )

    wall_bevel: FloatProperty(
        name='Wall Bevel',
        description="Add a bevel to the wall. Caution : This will increase generation time",
        default=0,
        min=0,
        soft_max=0.1,
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

    distance_color_start: FloatVectorProperty(
        name='Path Start Color',
        description="Change the path's start cell color. This will change the distance's displayed gradient",
        subtype='COLOR',
        default=(0, 1, 0),
        min=0,
        max=1,
        update=update_paint
    )

    distance_color_end: FloatVectorProperty(
        name='Path End Color',
        description="Change the path's end cell color. This will change the distance's displayed gradient",
        subtype='COLOR',
        default=(1, 0, 0),
        min=0,
        max=1,
        update=update_paint
    )

    hue_shift: FloatProperty(
        name="Hue Shift",
        description="Tweak the color hue shift of the cells",
        default=0,
        min=0,
        max=1,
    )

    saturation_shift: FloatProperty(
        name="Saturation Shift",
        description="Tweak the color saturation shift of the cells",
        default=0,
        min=-1,
        max=1,
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

    cell_thickness: FloatProperty(
        name="Cell Thickness",
        description="Tweak the cell's thickness",
        default=0,
        soft_max=1,
        soft_min=0,
    )

    cell_contour: FloatProperty(
        name='Cell Contour',
        description='This will add a stylised contour the cells',
        default=0,
        min=0,
        soft_max=0.2
    )

    value_shift: FloatProperty(
        name="Color Shift",
        description="Tweak the color value shift of the cells",
        default=0,
        min=-1,
        max=1,
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

    def register():
        Scene.mg_props = PointerProperty(type=MGProperties)

    def unregister():
        del Scene.mg_props
