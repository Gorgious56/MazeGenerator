def update_mesh_smooth(mesh, use_smooth):
    mesh.polygons.foreach_set("use_smooth", [use_smooth] * len(mesh.polygons))
    mesh.update()
