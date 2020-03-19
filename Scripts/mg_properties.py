from bpy.types import PropertyGroup, Scene
from bpy.props import IntProperty, BoolProperty, EnumProperty, FloatProperty, PointerProperty
from . maze_logic . algorithms . algorithm_manager import generate_algo_enum, DEFAULT_ALGO


class MGProperties(PropertyGroup):
    use_polar_grid: BoolProperty(
        name='Use Polar Grid',
        description='Check this if you want to use circular coordinates',
    )

    maze_algorithm: EnumProperty(
        name="Algorithm",
        description="Choose which algorithm will generate the maze",
        items=generate_algo_enum(),
        default=DEFAULT_ALGO
    )

    rows_or_radius: IntProperty(
        name="Rows | Radius",
        description="Choose the size along the y axis or the radius if using polar coordinates",
        default=5,
        min=1,
        soft_max=100
    )

    seed: IntProperty(
        name="Seed",
        description="This seed will be used to randomize the maze",
        default=0,
        # update=lambda self, context: print(context.seed)
    )

    wall_height: FloatProperty(
        name="Height",
        description="Configure the wall default height",
        default=0.5,
        min=0
    )

    wall_width: FloatProperty(
        name="Width",
        description="Configure the wall default width",
        default=0.2,
        min=0,
        soft_max=2
    )

    def register():
        Scene.mg_props = PointerProperty(type=MGProperties)

    def unregister():
        del Scene.mg_props
