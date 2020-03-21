from bpy.types import PropertyGroup, Scene
from bpy.props import IntProperty, BoolProperty, EnumProperty, FloatProperty, PointerProperty, FloatVectorProperty
import bpy.ops
from . maze_logic . algorithms . algorithm_manager import generate_algo_enum, DEFAULT_ALGO
from . visual . cell_type_manager import generate_cell_type_enum, DEFAULT_CELL_TYPE
from . visual . grid_visual import GridVisual
from random import random


def generate_maze(self, context):
    if self.auto_update and context.mode == "OBJECT":
        bpy.ops.maze.generate()


def update_paint(self, context):
    print(GridVisual.Instance)
    if GridVisual.Instance:
        GridVisual.Instance.set_materials()


def click_randomize_color_button(self, value):
    self.seed_color = random() * 100000
    if GridVisual.Instance:
        GridVisual.Instance.set_materials()
        GridVisual.Instance.paint_cells()


class MGProperties(PropertyGroup):
    auto_update: BoolProperty(
        name='Auto Update',
        default=True,
        description='Generate a new maze each time a property is modified',
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
        description="Choose the shape of your cells",
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
        description="Set the amount of dead-ends to get rid of",
        default=0,
        min=0,
        max=100,
        subtype='PERCENTAGE',
        options={'ANIMATABLE'},
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
        items=[
            ('DISTANCE', 'Distance', ''),
            ('GROUP', 'Cell Group', ''),
            ('UNIFORM', 'Uniform', ''),
            ('NEIGHBORS', 'Neighbors Amount', ''),
        ],
        default='DISTANCE',
        update=update_paint
    )

    def register():
        Scene.mg_props = PointerProperty(type=MGProperties)

    def unregister():
        del Scene.mg_props
