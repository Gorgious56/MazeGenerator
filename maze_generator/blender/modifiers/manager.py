"""
Manager module for object modifiers
"""

import bpy.types
import bpy.props
from .objects import cells as cells_mods
from .objects import walls as walls_mods


def setup_modifiers(scene, props) -> None:
    cells_mods.setup_modifiers(scene, props)
    walls_mods.setup_modifiers(scene, props)


class ModifierNamesPropertyGroup(bpy.types.PropertyGroup):
    """
    Property group storing modifier names
    """

    bevel: bpy.props.StringProperty(
        default="MG_BEVEL",
    )
    cylinder: bpy.props.StringProperty(
        default="MG_CYLINDER",
    )
    decimate: bpy.props.StringProperty(
        default="MG_DECIMATE",
    )
    mask: bpy.props.StringProperty(
        default="MG_MASK_STAIRS",
    )
    mask_longest_path: bpy.props.StringProperty(
        default="MG_MASK_PATH",
    )
    mask_sparse: bpy.props.StringProperty(
        default="MG_MASK_SPARSE",
    )
    moebius: bpy.props.StringProperty(
        default="MG_MOEBIUS",
    )
    screw: bpy.props.StringProperty(
        default="MG_SCREW",
    )
    solid: bpy.props.StringProperty(
        default="MG_SOLIDIFY",
    )
    stairs: bpy.props.StringProperty(
        default="MG_STAIRS",
    )
    subdiv: bpy.props.StringProperty(
        default="MG_SUBSURF",
    )
    texture_disp: bpy.props.StringProperty(
        default="MG_TEX_DISP",
    )
    torus: bpy.props.StringProperty(
        default="MG_TORUS",
    )
    thickness_disp: bpy.props.StringProperty(
        default="MG_THICK_DISP",
    )
    thickness_solid: bpy.props.StringProperty(
        default="M_THICKNESS_SOLID",
    )
    thickness_shrinkwrap: bpy.props.StringProperty(
        default="MG_THICK_SHRINKWRAP",
    )
    vert_weight_prox: bpy.props.StringProperty(
        default="MG_WEIGHT_PROX",
    )
    weave_disp: bpy.props.StringProperty(
        default="MG_WEAVE_DISPLACE",
    )
    weld: bpy.props.StringProperty(
        default="MG_WELD",
    )
    wireframe: bpy.props.StringProperty(
        default="MG_WIREFRAME",
    )


# M_WELD_2 = 'MG_WELD_2'
# M_THICKNESS_SOLID = 'MG_THICK_SOLID'
# M_WEAVE_MIX = 'MG_WEAVE_MIX'
# M_DECIMATE_PLANAR = 'MG_DECIMATE_PLANAR'
# M_CYLINDER_WELD = 'MG_CYLINDER_WELD'
# M_MASK_SPARSE = 'MG_MASK_SPARSE'
# M_SMOOTH_CENTER_NAME = 'MG_SMOOTH_CENTER'
# M_SMOOTH_BRIDGE_COL_X_NAME, M_SMOOTH_BRIDGE_COL_Y_NAME = 'MG_SMOOTH_BRIDGE_COL_X', 'MG_SMOOTH_BRIDGE_COL_Y'
# M_SMOOTH_BRIDGE_ROW_X_NAME, M_SMOOTH_BRIDGE_ROW_Y_NAME = 'MG_SMOOTH_BRIDGE_ROW_X', 'MG_SMOOTH_BRIDGE_ROW_Y'
# M_MASK_BRIDGE = 'MG_MASK_BRIDGE'

# VISIBILIY = 'VISIBILITY'
