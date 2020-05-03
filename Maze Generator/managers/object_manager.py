import bpy
from typing import List
import math


def link_objects_to_collection(
        objects: List[bpy.types.Object],
        new_col: bpy.types.Collection,
        unlink_from_existing: bool = True) -> None:
    for obj in (obj for obj in objects if obj):
        if unlink_from_existing:
            for col in obj.users_collection:
                col.objects.unlink(obj)
        if obj.name not in new_col.objects:
            new_col.objects.link(obj)


def get_or_create_mesh_object(
        parent,
        get_object: callable,
        obj_attr_name: str,
        obj_name: str) -> None:
    mesh = bpy.data.meshes.get(obj_name)
    if not mesh:
        mesh = bpy.data.meshes.new(obj_name)
    obj = get_object(obj_name)
    if not obj:
        obj = bpy.data.objects.new(obj_name, mesh)
    setattr(parent, obj_attr_name, obj)


def get_or_create_helper(
        parent,
        get_object: callable,
        attr_name: str,
        obj_name: str,
        primitive_add=bpy.ops.curve.primitive_bezier_circle_add, rot:
        float = (0, 0, 0), attributes=None) -> None:
    if hasattr(parent, attr_name):
        obj_get = get_object(obj_name)
        if not obj_get:
            primitive_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), rotation=rot)
            obj_get = bpy.context.active_object
            obj_get.name = obj_name
            obj_get.data.name = obj_name
        if attributes:
            for obj_attr, obj_attr_value in attributes.items():
                setattr(obj_get, obj_attr, obj_attr_value)
        setattr(parent, attr_name, obj_get)
        obj_get.hide_viewport = obj_get.hide_render = True


class ObjectManager:
    col_objects = None
    obj_walls = None
    obj_cells = None
    obj_cylinder = None
    obj_torus = None
    obj_thickness_shrinkwrap = None

    @property
    def mesh_walls():
        return ObjectManager.obj_walls.data if ObjectManager.obj_walls else None

    @property
    def mesh_cells():
        return ObjectManager.obj_cells.data if ObjectManager.obj_cells else None

    def get_or_create_and_link_objects(scene) -> None:
        self = ObjectManager
        self.col_objects = bpy.data.collections.get('MG_Collection')
        if not self.col_objects:
            self.col_objects = bpy.data.collections.new(name='MG_Collection')
        if self.col_objects.name not in scene.collection.children:
            scene.collection.children.link(self.col_objects)

        get_or_create_mesh_object(self, scene.objects.get, 'obj_walls', 'MG_Walls')
        get_or_create_mesh_object(self, scene.objects.get, 'obj_cells', 'MG_Cells')

        get_or_create_helper(self, scene.objects.get, 'obj_thickness_shrinkwrap', 'MG_Thickness_SW', bpy.ops.mesh.primitive_plane_add, attributes={'scale': [10000] * 3})
        get_or_create_helper(self, scene.objects.get, 'obj_cylinder', 'MG_Curver_Cyl', rot=(math.pi / 2, 0, 0))
        get_or_create_helper(self, scene.objects.get, 'obj_torus', 'MG_Curver_Tor')

        link_objects_to_collection(
            (self.obj_cells, self.obj_cylinder, self.obj_walls, self.obj_torus, self.obj_thickness_shrinkwrap),
            self.col_objects)

    def update_wall_visibility(props, is_algo_weaved) -> None:
        ObjectManager.obj_walls.hide_viewport = ObjectManager.obj_walls.hide_render = \
            props.wall_hide or (props.maze_weave and is_algo_weaved)
