import bpy.ops
from bpy.types import PropertyGroup, Scene
from bpy.props import IntProperty, BoolProperty, EnumProperty, FloatProperty, PointerProperty, IntVectorProperty
from .managers.algorithm_manager import generate_algo_enum, is_algo_weaved, DEFAULT_ALGO
from .managers.cell_type_manager import generate_cell_type_enum, DEFAULT_CELL_TYPE
from .managers.space_rep_manager import generate_space_rep_enum, REP_REGULAR
from .managers.mesh_manager import generate_cell_visual_enum, DEFAULT_CELL_VISUAL_TYPE
from .visual.maze_visual import MazeVisual
from .managers.object_manager import ObjectManager
from .managers import mesh_manager, material_manager, modifier_manager


def generate_maze(self, context) -> None:
    if self.auto_update and context.mode == "OBJECT":
        bpy.ops.maze.generate()


def update_inset(self, context) -> None:
    generate_maze(self, context)


def update_paint(self, context: bpy.types.Context) -> None:
    material_manager.MaterialManager.set_materials(self, context.scene)
    if not self.show_longest_path:
        ObjectManager.obj_cells.modifiers[modifier_manager.M_MASK_LONGEST_PATH].show_viewport = False


def update_modifiers(self, context) -> None:
    MazeVisual.generate_modifiers()
    MazeVisual.generate_drivers()


def update_cell_type(self, context: bpy.types.Context) -> None:
    reset_enum = True
    for ind, _, _ in generate_space_rep_enum(self, context):
        if self.maze_space_dimension == ind:
            reset_enum = False
            break
    if reset_enum:
        print('Do not worry about these warnings.')
        self['maze_space_dimension'] = REP_REGULAR
    generate_maze(self, context)


def toggle_maze_weave(self, context) -> None:
    if self.maze_weave_toggle:
        if self.maze_weave == 0:
            self.maze_weave = 50
    else:
        self.maze_weave = 0


def update_objects_visibility(self, context) -> None:
    ObjectManager.update_wall_visibility(self, is_algo_weaved(self))


def tweak_maze_weave(self, context: bpy.types.Context) -> None:
    self['maze_weave_toggle'] = self.maze_weave > 0
    generate_maze(self, context)


def update_prop(self, value, prop_name):
    if hasattr(self, prop_name):
        setattr(self, prop_name, value)


class MGProperties(PropertyGroup):
    show_gizmos: BoolProperty(
        name="Show Gizmos",
        default=True,
        description="Check this to display the interactive gizmos",
    )

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
        update=lambda self, context: mesh_manager.MeshManager.update_smooth(self, ObjectManager.obj_cells.data, ObjectManager.obj_walls.data)
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
        set=lambda self, value: update_prop(self, value * 2, "maze_rows_or_radius"),
    )

    maze_columns: IntProperty(
        name="Columns",
        description="Choose the size along the X axis",
        default=10,
        min=2,
        soft_max=100,
        update=generate_maze
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

    maze_random_path: BoolProperty(
        name="Random Path",
        default=True,
    )

    maze_outside_path: BoolProperty(
        name="Force Outside Path",
        description="Force the maze solution to start and end on the outside of the maze",
        default=False,
    )

    maze_force_start: IntVectorProperty(
        name="Start Maze Here",
        size=2,
    )

    maze_force_end: IntVectorProperty(
        name="End Maze Here",
        size=2,
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

    def register():
        Scene.mg_props = PointerProperty(type=MGProperties)

    def unregister():
        del Scene.mg_props
