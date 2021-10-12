import bpy
import math
from maze_generator.blender.collection.helper import link_objects_to_collection
from maze_generator.blender.object.helper import (
    get_or_create_mesh_object,
    get_or_create_helper,
)


def get_or_create_and_link_objects(scene) -> None:
    props = scene.mg_props

    props_col = props.collections
    col = props_col.objects
    if not col:
        col = bpy.data.collections.get(props_col.objects_name)
    if not col:
        col = bpy.data.collections.new(name=props_col.objects_name)
    props_col.objects = col
    if col.name not in scene.collection.children:
        scene.collection.children.link(col)

    get_or_create_mesh_object(props, scene.objects.get, "walls", "MG_Walls")
    get_or_create_mesh_object(props, scene.objects.get, "cells", "MG_Cells")

    get_or_create_helper(
        props,
        scene.objects.get,
        "thickness_shrinkwrap",
        "MG_Thickness_SW",
        bpy.ops.mesh.primitive_plane_add,
        attributes={"scale": [10000] * 3},
    )
    get_or_create_helper(props, scene.objects.get, "cylinder", "MG_Curver_Cyl", rot=(math.pi / 2, 0, 0))
    get_or_create_helper(props, scene.objects.get, "torus", "MG_Curver_Tor")

    link_objects_to_collection(
        (
            props.objects.cells,
            props.objects.walls,
            props.objects.cylinder,
            props.objects.torus,
            props.objects.thickness_shrinkwrap,
        ),
        col,
    )
