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


class InteractionPropertyGroup(bpy.types.PropertyGroup):
    """
    Property group storing interaction parameters
    """

    show_gizmos: BoolProperty(
        name="Show Gizmos",
        default=True,
        description="Check this to display the interactive gizmos",
    )
