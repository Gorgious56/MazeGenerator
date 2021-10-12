import bpy
from bpy.props import (
    IntProperty,
    BoolProperty,
    EnumProperty,
    FloatProperty,
    PointerProperty,
    StringProperty,
    IntVectorProperty,
)
from maze_generator.maze.algorithm.algorithms import (
    generate_algo_enum,
    is_algo_weaved,
    DEFAULT_ALGO,
)
from maze_generator.blender.generation.main import generate_maze


class AlgorithmPropertyGroup(bpy.types.PropertyGroup):
    """
    Property group storing algorithm parameters
    """

    algorithm: EnumProperty(
        name="Algorithm",
        description="Choose which algorithm will generate the maze",
        items=generate_algo_enum(),
        default=DEFAULT_ALGO,
        update=generate_maze,
    )

    seed: IntProperty(
        name="Seed", description="This seed will be used to randomize the maze", default=0, update=generate_maze
    )

    bias: FloatProperty(
        name="Bias",
        description="Add a bias to the algorithm in a certain direction",
        default=0,
        soft_min=-1,
        soft_max=1,
        subtype="FACTOR",
        update=generate_maze,
    )

    room_size: IntProperty(
        name="Room Size",
        description="tweak this to stop the recursive division when the room size is lower than the number",
        default=5,
        min=2,
        soft_max=200,
        update=generate_maze,
    )

    room_size_deviation: IntProperty(
        name="Room Size Deviation",
        description="tweak this to add randomness to the room size property. At a value of 1, the room size will vary between the minimum and the value in the room property",
        default=0,
        min=0,
        soft_max=100,
        subtype="PERCENTAGE",
        update=generate_maze,
    )

    sparse_dead_ends: IntProperty(
        name="Sparse Maze",
        description="Choose how many dead ends will be culled subsequently to make a sparser maze",
        default=0,
        min=0,
        max=100,
        subtype="PERCENTAGE",
        update=generate_maze,
    )

    keep_dead_ends: IntProperty(
        name="Braid Dead Ends",
        description="This percentage of dead-ends will be connected to one of their neighbors",
        default=100,
        min=0,
        max=100,
        subtype="PERCENTAGE",
        update=generate_maze,
    )
