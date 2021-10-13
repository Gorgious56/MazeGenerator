import bpy
from maze_generator.blender.mesh.vertex_groups.helper import (
    ensure_vertex_groups_exist,
    rename_vertex_group,
    update_vertex_group_in_modifiers,
)


def ensure_vertex_groups(objects, vertex_groups_props):
    for obj in (objects.cells, objects.walls):
        ensure_vertex_groups_exist(obj, vertex_groups_props.names)


def get_vg_name(self, attr, default):
    return self.get(attr, default)


def set_vg_name(self, attr, value):
    if value == "" or value in self.names:
        return
    old_value = getattr(self, attr)
    mg_props = bpy.context.scene.mg_props
    for obj in (mg_props.objects.cells, mg_props.objects.walls):
        rename_vertex_group(obj, old_value, value)
        update_vertex_group_in_modifiers(obj, old_value, value)
    self[attr] = value
