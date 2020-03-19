from bpy.types import PropertyGroup, Scene
from bpy.props import IntProperty, BoolProperty, EnumProperty, PointerProperty
from . algorithm_names import generate_algo_enum, DEFAULT_ALGO


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

    def register():
        Scene.mg_props = PointerProperty(type=MGProperties)

    def unregister():
        del Scene.mg_props
