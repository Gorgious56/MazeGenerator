from bpy.types import PropertyGroup, Scene
from bpy.props import IntProperty, BoolProperty, EnumProperty, FloatProperty, PointerProperty
import bpy.ops
from . maze_logic . algorithms . algorithm_manager import generate_algo_enum, DEFAULT_ALGO


def update_property(self, context):
    if self.auto_update:
        bpy.ops.maze.generate()


class MGProperties(PropertyGroup):
    auto_update: BoolProperty(
        name='Auto Update',
        description='Generate a new maze each time a property is modified',
        update=update_property
    )

    use_polar_grid: BoolProperty(
        name='Use Polar Grid',
        description='Check this if you want to use circular coordinates',
        update=update_property
    )

    maze_algorithm: EnumProperty(
        name="Algorithm",
        description="Choose which algorithm will generate the maze",
        items=generate_algo_enum(),
        default=DEFAULT_ALGO,
        update=update_property
    )

    rows_or_radius: IntProperty(
        name="Rows | Radius",
        description="Choose the size along the y axis or the radius if using polar coordinates",
        default=5,
        min=1,
        soft_max=100,
        update=update_property
    )

    seed: IntProperty(
        name="Seed",
        description="This seed will be used to randomize the maze",
        default=0,
        update=update_property
    )

    steps: IntProperty(
        name="Steps",
        description="Set the number of steps at which to stop the algorithm (0 = unlimited)",
        default=0,
        min=0,
        soft_max=10000,
        update=update_property
    )

    braid_dead_ends: FloatProperty(
        name="Braid Dead Ends",
        description="Set the amount of dead-ends to get rid of",
        default=0,
        min=0,
        max=1,
        update=update_property
    )

    wall_height: FloatProperty(
        name="Height",
        description="Configure the wall default height",
        default=0.5,
        min=0,
        update=update_property
    )

    wall_width: FloatProperty(
        name="Width",
        description="Configure the wall default width",
        default=0.2,
        min=0,
        soft_max=2,
        update=update_property
    )

    color_shift: FloatProperty(
        name="Color Shift",
        description="Tweak the color hue shift of the cells",
        default=0,
        min=0,
        max=1,
        update=update_property
    )
    

    def register():
        Scene.mg_props = PointerProperty(type=MGProperties)

    def unregister():
        del Scene.mg_props
