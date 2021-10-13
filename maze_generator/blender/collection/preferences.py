import bpy

def update_coll_name(self, context, attr):
    collection = getattr(context.scene.mg_props.collections, attr)
    if collection:
        collection.name = getattr(self, attr)


class CollectionsNamesPG(bpy.types.PropertyGroup):
    objects: bpy.props.StringProperty(
        name="Objects",
        default="MG_Collection",
        update=lambda s, c: update_coll_name(s, c, "objects"),
    )
    helpers: bpy.props.StringProperty(
        name="Helpers",
        default="MG_Helpers",
        update=lambda s, c: update_coll_name(s, c, "helpers"),
    )

    attributes_names = (
        "objects",
        "helpers",
    )
