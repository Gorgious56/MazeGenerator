def ensure_vertex_groups_exist(obj, vg_names):
    for vg_name in vg_names:
        ensure_vertex_group_exists(obj, vg_name)


def ensure_vertex_group_exists(obj, vg_name):
    if get_vertex_group_index(obj, vg_name) < 0:
        obj.vertex_groups.new(name=vg_name)


def rename_vertex_group(obj, old_name, new_name):
    for vg in obj.vertex_groups:
        if vg.name == old_name:
            vg.name = new_name
            break


def update_vertex_group_in_modifiers(obj, old_value, new_value):
    for mod in obj.modifiers:
        for mod_attr in dir(mod):
            if "vertex_group" not in mod_attr:
                continue
            if getattr(mod, mod_attr) == old_value:
                setattr(mod, mod_attr, new_value)


def get_vertex_group_index(obj, vg_name):
    for i, vg in enumerate(obj.vertex_groups):
        if vg.name == vg_name:
            return i
    return -1
