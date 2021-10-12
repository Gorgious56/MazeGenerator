from enum import Enum
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
from maze_generator.blender.generation.main import generate_maze
from maze_generator.maze.space_representation.prop import generate_space_rep_enum
from maze_generator.maze.cell.constants import CellType
from maze_generator.maze.space_representation.constants import SpaceRepresentation


def update_cell_type(self, context: bpy.types.Context) -> None:
    reset_enum = True

    for ind, _, _ in generate_space_rep_enum(self, context):
        if context.scene.mg_props.space_rep_props.representation == ind:
            reset_enum = False
            break
    if reset_enum:
        print("Do not worry about these warnings.")
        context.mg_props.space_rep_props["representation"] = SpaceRepresentation.PLANE.value
    generate_maze(self, context)


class CellPropertyGroup(bpy.types.PropertyGroup):
    """
    Property group storing cell parameters
    """

    inset: FloatProperty(
        name="Cell Inset",
        description="Tweak the cell's inset",
        default=0,
        soft_max=0.9,
        min=0,
        max=1,
        update=generate_maze,
    )

    type: EnumProperty(
        name="Cell Type",
        description="The shape of the maze's cells",
        items=CellType.get_type_enum(),
        default=CellType.DEFAULT.value,
        update=update_cell_type,
    )

    cell_decimate: IntProperty(
        name="Cell Decimate",
        description="Set the ratio of faces to decimate.",
        default=0,
        min=0,
        max=100,
        subtype="PERCENTAGE",
    )

    cell_contour: FloatProperty(name="Cell Bevel", description="Add bevel to the cells", default=0, min=0, soft_max=0.2)

    cell_contour_black: BoolProperty(
        name="Cell Contour", description="This will add a stylised black contour to the cells", default=False
    )

    def is_a(self, cell_type: Enum) -> bool:
        return self.type == cell_type.value
