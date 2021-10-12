import bpy
from bpy.props import StringProperty


class ModifierNamesPropertyGroup(bpy.types.PropertyGroup):
    """
    Property group storing modifier names
    """

    bevel: StringProperty(
        default="MG_BEVEL",
    )
    cylinder: StringProperty(
        default="MG_CYLINDER",
    )
    decimate: StringProperty(
        default="MG_DECIMATE",
    )
    mask: StringProperty(
        default="MG_MASK_STAIRS",
    )
    mask_longest_path: StringProperty(
        default="MG_MASK_PATH",
    )
    mask_sparse: StringProperty(
        default="MG_MASK_SPARSE",
    )
    moebius: StringProperty(
        default="MG_MOEBIUS",
    )
    screw: StringProperty(
        default="MG_SCREW",
    )
    solid: StringProperty(
        default="MG_SOLIDIFY",
    )
    stairs: StringProperty(
        default="MG_STAIRS",
    )
    subdiv: StringProperty(
        default="MG_SUBSURF",
    )
    texture_disp: StringProperty(
        default="MG_TEX_DISP",
    )
    torus: StringProperty(
        default="MG_TORUS",
    )
    thickness_disp: StringProperty(
        default="MG_THICK_DISP",
    )
    thickness_solid: StringProperty(
        default="M_THICKNESS_SOLID",
    )
    thickness_shrinkwrap: StringProperty(
        default="MG_THICK_SHRINKWRAP",
    )
    vert_weight_prox: StringProperty(
        default="MG_WEIGHT_PROX",
    )
    weave_disp: StringProperty(
        default="MG_WEAVE_DISPLACE",
    )
    weld: StringProperty(
        default="MG_WELD",
    )
    wireframe: StringProperty(
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