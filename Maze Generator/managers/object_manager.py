import bpy
from typing import List
import math


class ObjectManager:
    col_objects = None
    obj_walls = None
    mesh_walls = None
    obj_cells = None
    mesh_cells = None
    obj_cylinder = None
    obj_torus = None
    obj_thickness_shrinkwrap = None

    def generate_objects(scene) -> None:
        self = ObjectManager
        self.col_objects = bpy.data.collections.get('MG_Collection', bpy.data.collections.new(name='MG_Collection'))
        if self.col_objects.name not in scene.collection.children:
            scene.collection.children.link(self.col_objects)

        self.get_or_create_mesh_object(scene.objects.get, 'mesh_wall', 'MG_Wall Mesh', 'obj_walls', 'MG_Walls')
        self.get_or_create_mesh_object(scene.objects.get, 'mesh_cells', 'MG_Cells Mesh', 'obj_cells', 'MG_Cells')

        self.get_or_create_helper(scene.objects.get, 'obj_thickness_shrinkwrap', 'MG_Thickness_SW', bpy.ops.mesh.primitive_plane_add, attributes={'scale': [10000] * 3})
        self.get_or_create_helper(scene.objects.get, 'obj_cylinder', 'MG_Curver_Cyl', rot=(math.pi / 2, 0, 0))
        self.get_or_create_helper(scene.objects.get, 'obj_torus', 'MG_Curver_Tor')

        self.link_objects_to_collection((self.obj_cells, self.obj_cylinder, self.obj_walls, self.obj_torus, self.obj_thickness_shrinkwrap), self.col_objects)

    def get_or_create_mesh_object(get_object: callable, mesh_attr_name: str, mesh_name: str, obj_attr_name: str, obj_name: str) -> None:
        self = ObjectManager
        setattr(self, mesh_attr_name, bpy.data.meshes.get(mesh_name, bpy.data.meshes.new(mesh_name)))
        setattr(self, obj_attr_name, get_object(obj_name, bpy.data.objects.new(obj_name, getattr(self, mesh_attr_name))))

    def get_or_create_helper(get_object: callable, attr_name: str, obj_name: str, primitive_add=bpy.ops.curve.primitive_bezier_circle_add, rot: float = (0, 0, 0), attributes=None) -> None:
        self = ObjectManager
        if hasattr(self, attr_name):
            obj_get = get_object(obj_name)
            if not obj_get:
                primitive_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), rotation=rot)
                obj_get = bpy.context.active_object
                obj_get.name = obj_name
            if attributes:
                for obj_attr, obj_attr_value in attributes.items():
                    setattr(obj_get, obj_attr, obj_attr_value)
            setattr(self, attr_name, obj_get)
            obj_get.hide_viewport = obj_get.hide_render = True

    def link_objects_to_collection(objects: List[bpy.types.Object], new_col: bpy.types.Collection, unlink_from_existing: bool = True) -> None:
        for obj in (obj for obj in objects if obj):
            if unlink_from_existing:
                for col in obj.users_collection:
                    col.objects.unlink(obj)
            if obj.name not in new_col.objects:
                new_col.objects.link(obj)

    def update_wall_visibility(props, is_algo_weaved) -> None:
        ObjectManager.obj_walls.hide_viewport = ObjectManager.obj_walls.hide_render = \
            props.wall_hide \
            or (props.maze_weave and is_algo_weaved)
