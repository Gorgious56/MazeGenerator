import bpy


def update_objects_coll_name(self, context):
    if self.objects:
        self.objects.name = self.objects_name


class CollectionsPropertyGroup(bpy.types.PropertyGroup):
    """
    Stores the collections used in the add-on
    """

    objects: bpy.props.PointerProperty(name="Collection storing the add-on's objects", type=bpy.types.Collection)
    objects_name: bpy.props.StringProperty(
        name="Objects Collection Name", default="MG_Collection", update=update_objects_coll_name
    )
