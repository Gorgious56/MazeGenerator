"""
Contains definitions and methods to store and access Meshes
"""


import bpy


class MeshesPropertyGroup(bpy.types.PropertyGroup):    
    """
    Stores the meshes used in the add-on
    """
    walls: bpy.props.PointerProperty(
        name="Wall Mesh",
        type=bpy.types.Mesh)
    cells: bpy.props.PointerProperty(
        name="Cells Mesh",
        type=bpy.types.Mesh)
