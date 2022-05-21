def ensure_test_mesh(mesh):
    mesh.clear_geometry()
    verts = []
    for x in range(10):
        for y in range(10):
            verts.append((x, y, 0))
    mesh.from_pydata(verts, (), ())
