from bpy.types import PropertyGroup, Scene
from bpy.props import IntProperty, BoolProperty, EnumProperty, FloatProperty, PointerProperty, FloatVectorProperty
import bpy.ops
from . maze_logic . algorithms . algorithm_manager import generate_algo_enum, DEFAULT_ALGO
from . visual . cell_type_manager import generate_cell_type_enum, DEFAULT_CELL_TYPE
from . visual . cell_visual_manager import generate_cell_visual_enum, DEFAULT_CELL_VISUAL_TYPE
from . visual . grid_visual import GridVisual
from random import random


def generate_maze(self, context):
    if self.auto_update and context.mode == "OBJECT":
        bpy.ops.maze.generate()


def update_paint(self, context):
    if GridVisual.Instance:
        GridVisual.Instance.set_materials()
        GridVisual.Instance.update_visibility()


def click_randomize_color_button(self, value):
    self.seed_color = random() * 100000
    if GridVisual.Instance:
        GridVisual.Instance.set_materials()
        GridVisual.Instance.paint_cells()


class MGProperties(PropertyGroup):
    auto_update: BoolProperty(
        name='Auto Update',
        default=True,
        description='Generate a new maze each time a parameter is modified. This will hurt performance when generating big mazes',
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
        # update=generate_maze
    )

    wall_width: FloatProperty(
        name="Width",
        description="Configure the wall default width",
        default=0.2,
        min=0,
        soft_max=2,
        # update=generate_maze
    )

    wall_color: FloatVectorProperty(
        name='Wall Color',
        description="Change the wall's displayed color",
        subtype='COLOR',
        default=(0.5, 0.5, 0.5),
        min=0,
        max=1,
        update=update_paint
    )

    wall_hide: BoolProperty(
        name='Wall Hide',
        description="Auto-hide the wall if the cells are inset",
        default=True,
        update=update_paint
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

    cell_size: FloatProperty(
        name="Cell Size",
        description="Tweak the cell's size",
        default=1,
        soft_min=0.1,
        min=0,
        max=1,
        update=generate_maze
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



    def register():
        Scene.mg_props = PointerProperty(type=MGProperties)

    def unregister():
        del Scene.mg_props
