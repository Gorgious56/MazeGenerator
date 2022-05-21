import bpy
import math
from maze_generator.blender.collection.helper import (
    link_objects_to_collection,
    get_or_create_collection,
)
from maze_generator.blender.object.tool import (
    get_or_create_mesh_object,
    get_or_create_helper,
)


def get_or_create_and_link_objects(scene, preferences) -> None:
    props = scene.mg_props

    props_col = props.collections

    col_objects = props_col.objects
    if not col_objects:
        col_objects = get_or_create_collection(scene, preferences.collections_names.objects)
        props_col.objects = col_objects

    get_or_create_mesh_object(props, scene.objects.get, "walls", preferences.objects_names.walls)
    get_or_create_mesh_object(props, scene.objects.get, "cells", preferences.objects_names.cells)

    link_objects_to_collection(
        (
            props.objects.cells,
            props.objects.walls,
        ),
        col_objects,
    )

    col_helpers = props_col.helpers
    if not col_helpers:
        col_helpers = get_or_create_collection(scene, preferences.collections_names.helpers)
        props_col.helpers = col_helpers
    if col_helpers.name not in col_objects.children:
        col_objects.children.link(col_helpers)
        if col_helpers.name in scene.collection.children:
            scene.collection.children.unlink(col_helpers)

    get_or_create_helper(
        props,
        scene.objects.get,
        "thickness_shrinkwrap",
        preferences.objects_names.thickness_shrinkwrap,
        bpy.ops.mesh.primitive_plane_add,
        attributes={"scale": [10000] * 3},
    )
    get_or_create_helper(
        props, scene.objects.get, "cylinder", preferences.objects_names.cylinder, rot=(math.pi / 2, 0, 0)
    )
    get_or_create_helper(props, scene.objects.get, "torus", preferences.objects_names.torus)

    link_objects_to_collection(
        (
            props.objects.cylinder,
            props.objects.torus,
            props.objects.thickness_shrinkwrap,
        ),
        col_helpers,
    )
