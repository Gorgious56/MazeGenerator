def ensure_vertex_group_exists(obj, vg_name):
    # TODO : Try / except ? next()
    vg_exists = False
    for _vg in obj.vertex_groups:
        if _vg.name == vg_name:
            vg_exists = True
            break
    if not vg_exists:
        obj.vertex_groups.new(name=vg_name)

def ensure_vertex_groups_exist(obj, vg_names):
    for vg_name in vg_names:
        ensure_vertex_group_exists(obj, vg_name)

def update_mesh_smooth(mesh, use_smooth):
    mesh.polygons.foreach_set("use_smooth", [use_smooth] * len(mesh.polygons))
    mesh.update()
