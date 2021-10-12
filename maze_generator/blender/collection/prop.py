import bpy


class CollectionsPropertyGroup(bpy.types.PropertyGroup):
    """
    Stores the collections used in the add-on
    """

    objects: bpy.props.PointerProperty(name="Collection storing the add-on's objects", type=bpy.types.Collection)
