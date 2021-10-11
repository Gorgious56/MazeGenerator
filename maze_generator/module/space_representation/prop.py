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
from maze_generator.blender.properties.updates import generate_maze
from maze_generator.module.cell.constants import CellType
from maze_generator.module.space_representation.constants import SpaceRepresentation


def generate_space_rep_enum(self, context):
    generate_space_rep_enum.enum.clear()
    # space_reps = self.space_reps
    ret = [(SpaceRepresentation.PLANE.value, SpaceRepresentation.PLANE.name.capitalize(), "")]
    if not context.scene.mg_props.cell_props.is_a(CellType.POLAR):
        ret.extend(
            (
                (SpaceRepresentation.CYLINDER.value, SpaceRepresentation.CYLINDER.name.capitalize(), ""),
                (SpaceRepresentation.MOEBIUS.value, SpaceRepresentation.MOEBIUS.name.capitalize(), ""),
                (SpaceRepresentation.TORUS.value, SpaceRepresentation.TORUS.name.capitalize(), ""),
            )
        )
        # (space_reps.box, 'Box', '')))
    return ret


generate_space_rep_enum.enum = []


class SpaceRepPropertyGroup(bpy.types.PropertyGroup):
    """
    Property group storing Space Representation Parameters
    """

    representation: EnumProperty(
        name="Space representation",
        description="Choose if and how to fold the maze in 3D dimensions",
        items=generate_space_rep_enum,
        update=generate_maze,
    )
