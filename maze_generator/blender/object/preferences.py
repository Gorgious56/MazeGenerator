import bpy

def update_object_name(self, context, attr):
    object = getattr(context.scene.mg_props.objects, attr)
    if object:
        object.name = getattr(self, attr)
    mesh = getattr(context.scene.mg_props.meshes, attr)
    if mesh:
        mesh.name = getattr(self, attr)


class ObjectsNamesPG(bpy.types.PropertyGroup):
    walls: bpy.props.StringProperty(
        name="Wall",
        default="MG_Walls",
        update=lambda s, c: update_object_name(s, c, "walls"),
    )
    cells: bpy.props.StringProperty(
        name="Cells",
        default="MG_Cells",
        update=lambda s, c: update_object_name(s, c, "cells"),
    )
    cylinder: bpy.props.StringProperty(
        name="Cylinder",
        default="MG_Curver_Cyl",
        update=lambda s, c: update_object_name(s, c, "cylinder"),
    )
    torus: bpy.props.StringProperty(
        name="Torus",
        default="MG_Curver_Tor",
        update=lambda s, c: update_object_name(s, c, "torus"),
    )
    thickness_shrinkwrap: bpy.props.StringProperty(
        name="Shrinkwrap",
        default="MG_Thickness_SW",
        update=lambda s, c: update_object_name(s, c, "thickness_shrinkwrap"),
    )

    attributes_names = (
        "walls",
        "cells",
        "cylinder",
        "torus",
        "thickness_shrinkwrap",
    )
