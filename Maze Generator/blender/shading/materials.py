"""
This module sets properties of the materials
And handles accessing them
"""
import bpy


class MaterialsPropertyGroup(bpy.types.PropertyGroup):
    """
    Property group storing pointers to the materials
    """
    cell: bpy.props.PointerProperty(
        name="Cell Material",
        type=bpy.types.Material)
    wall: bpy.props.PointerProperty(
        name="Wall Material",
        type=bpy.types.Material)
