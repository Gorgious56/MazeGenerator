def ensure_vertex_groups_exist(obj, vg_names):
    for vg_name in vg_names:
        ensure_vertex_group_exists(obj, vg_name)


def ensure_vertex_group_exists(obj, vg_name):
    if get_vertex_group_index(obj, vg_name) < 0:
        obj.vertex_groups.new(name=vg_name)


def get_vertex_group_index(obj, vg_name):
    for i, _vg in enumerate(obj.vertex_groups):
        if _vg.name == vg_name:
            return i
    return -1
