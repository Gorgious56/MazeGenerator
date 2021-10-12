import bpy


class TexturesPropertyGroup(bpy.types.PropertyGroup):
    """
    Property group storing pointers to the textures
    """

    displacement: bpy.props.PointerProperty(name="Displacement", type=bpy.types.Texture)
