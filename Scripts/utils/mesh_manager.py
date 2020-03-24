import bmesh


def remove_all_vertex_layers(mesh):
    vertex_colors = mesh.vertex_colors
    while vertex_colors:
        vertex_colors.remove(vertex_colors[0])


def set_vertex_colors_layer(obj, bm, layer_name, cols, cell_corners=4):
    color_layer = bm.loops.layers.color.new(layer_name)

    homogen_grid = type(cell_corners) is not list
    if homogen_grid:
        color_table = [cols[i // cell_corners] for i in range(len(bm.verts))]
    else:
        color_table = []
        current_face = 0
        remaining_verts = cell_corners[current_face]
        for v in range(len(bm.verts)):
            color_table.append(cols[current_face])
            remaining_verts -= 1
            if remaining_verts == 0:
                current_face += 1
                try:
                    remaining_verts = cell_corners[current_face]
                except IndexError:
                    break

    for face in bm.faces:
        for loop in face.loops:
            loop[color_layer] = color_table[loop.vert.index]


def set_vertex_color_layers(obj, layers, cell_corners):
    # the layer parameter is supposed to be a dictionary with key = vertex layer name, and values = all cell colors
    mesh = obj.data
    remove_all_vertex_layers(mesh)

    # for g in obj.vertex_groups:
    #     obj.vertex_groups.remove(g)
    homogen_grid = type(cell_corners) is not list

    bm = bmesh.new()
    bm.from_mesh(mesh)

    for layer_name, cols in layers.items():
        if any(cols):
            if homogen_grid:
                # cell_corners = max(len(bm.verts) // len(cols), 3, cell_corners)
                set_vertex_colors_layer(obj, bm, layer_name, cols, cell_corners)
            else:
                set_vertex_colors_layer(obj, bm, layer_name, cols, cell_corners)

    bm.to_mesh(mesh)
