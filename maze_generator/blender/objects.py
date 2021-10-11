"""
This modules stores methods and properties related to Blender objects and collections
"""
import math
import bpy
from .collections import link_objects_to_collection


def get_or_create_mesh_object(props, get_object: callable, obj_attr_name: str, obj_name: str) -> None:
    mesh = bpy.data.meshes.get(obj_name)
    if not mesh:
        mesh = bpy.data.meshes.new(obj_name)

    setattr(props.meshes, obj_attr_name, mesh)
    obj = get_object(obj_name)
    if not obj:
        obj = bpy.data.objects.new(obj_name, mesh)

    setattr(props.objects, obj_attr_name, obj)


def get_or_create_helper(
    props,
    get_object: callable,
    attr_name: str,
    obj_name: str,
    primitive_add=bpy.ops.curve.primitive_bezier_circle_add,
    rot: float = (0, 0, 0),
    attributes=None,
) -> None:
    if not hasattr(props.objects, attr_name):
        return
    obj_get = get_object(obj_name)
    if not obj_get:
        primitive_add(enter_editmode=False, align="WORLD", location=(0, 0, 0), rotation=rot)
        obj_get = bpy.context.active_object
        obj_get.name = obj_name
        obj_get.data.name = obj_name
    setattr(props.objects, attr_name, obj_get)
    if attributes:
        for obj_attr, obj_attr_value in attributes.items():
            setattr(obj_get, obj_attr, obj_attr_value)
    obj_get.hide_viewport = obj_get.hide_render = True


def get_or_create_and_link_objects(scene) -> None:
    props = scene.mg_props

    col = bpy.data.collections.get("MG_Collection")
    if not col:
        col = bpy.data.collections.new(name="MG_Collection")
    props.collections.objects = col
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


def update_wall_visibility(props, is_algo_weaved) -> None:
    obj_walls = props.objects.walls
    obj_walls.hide_viewport = obj_walls.hide_render = props.wall_hide or (props.maze_weave and is_algo_weaved)


class ObjectsPropertyGroup(bpy.types.PropertyGroup):
    """
    Property group storing pointers to the objects
    """

    walls: bpy.props.PointerProperty(name="Wall Object", type=bpy.types.Object)
    cells: bpy.props.PointerProperty(name="Cells Object", type=bpy.types.Object)
    cylinder: bpy.props.PointerProperty(name="Cylinder Object", type=bpy.types.Object)
    torus: bpy.props.PointerProperty(name="Torus Object", type=bpy.types.Object)
    thickness_shrinkwrap: bpy.props.PointerProperty(name="Empty Object helping shrinkwrapping", type=bpy.types.Object)
