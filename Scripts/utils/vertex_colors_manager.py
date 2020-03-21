import bmesh


def remove_all_vertex_layers(mesh):
    vertex_colors = mesh.vertex_colors
    while vertex_colors:
        vertex_colors.remove(vertex_colors[0])


def set_vertex_colors_layer(obj, bm, layer_name, cols, points_per_face=4):

    color_layer = bm.loops.layers.color.new(layer_name)
    color_table = [cols[i // points_per_face] for i in range(len(bm.verts))]

    for face in bm.faces:
        for loop in face.loops:
            loop[color_layer] = color_table[loop.vert.index]


def set_vertex_color_layers(obj, layers, points_per_face=4):
    # the layer parameter is supposed to be a dictionary with key = vertex layer name, and values = all cell colors
    mesh = obj.data
    remove_all_vertex_layers(mesh)

    bm = bmesh.new()
    bm.from_mesh(mesh)   
    
    for layer_name, cols in layers.items():
        points_per_face = max(len(bm.verts) // len(cols), 3, points_per_face)
        set_vertex_colors_layer(obj, bm, layer_name, cols, points_per_face)

    bm.to_mesh(mesh)

# def set_vertex_colors(obj, cols, points_per_face=4):
#     mesh = obj.data
    
#     vertex_colors = mesh.vertex_colors
#     while vertex_colors:
#         vertex_colors.remove(vertex_colors[0])

#     bm = bmesh.new()
#     bm.from_mesh(mesh)

#     points_per_face = max(len(bm.verts) // len(cols), 3, points_per_face)

#     color_layer = bm.loops.layers.color.new("color")
#     color_table = [cols[i // points_per_face] for i in range(len(bm.verts))]

#     for face in bm.faces:
#         for loop in face.loops:
#             loop[color_layer] = color_table[loop.vert.index]

#     bm.to_mesh(mesh)

    # bm.verts.index_update()

    # for i, v in enumerate(bm.verts):
    #     v.index = i
