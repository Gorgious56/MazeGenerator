import bpy
from maze_generator.blender.mesh.vertex_groups.helper import ensure_vertex_groups_exist


def ensure_vertex_groups(objects, vertex_groups_props):
    for obj in (objects.cells, objects.walls):
        ensure_vertex_groups_exist(obj, vertex_groups_props.names)


def get_vg_name(self, attr, default):
    return self.get(attr, default)


def set_vg_name(self, attr, value):
    if value == "" or value in self.names:
        return
    self[attr] = value
