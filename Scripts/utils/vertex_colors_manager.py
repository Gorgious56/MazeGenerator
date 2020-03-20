import bmesh


def set_vertex_colors(obj, cols, points_per_face=4):
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)

    points_per_face = max(len(bm.verts) // len(cols), 3, points_per_face)

    color_layer = bm.loops.layers.color.new("color")
    color_table = [cols[i // points_per_face] for i in range(len(bm.verts))]

    for face in bm.faces:
        for loop in face.loops:
            loop[color_layer] = color_table[loop.vert.index]

    bm.to_mesh(mesh)

    bm.verts.index_update()

    for i, v in enumerate(bm.verts):
        v.index = i
