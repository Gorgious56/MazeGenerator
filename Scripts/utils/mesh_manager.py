import bmesh
from .. visual . cell_visual import VERTEX_GROUPS


def remove_all_vertex_layers(mesh):
    vertex_colors = mesh.vertex_colors
    while vertex_colors:
        vertex_colors.remove(vertex_colors[0])


def set_mesh_layers(obj, cells_visual):
    if cells_visual:
        mesh = obj.data
        remove_all_vertex_layers(mesh)

        bm = bmesh.new()
        bm.from_mesh(mesh)

        color_tables = {}
        color_layers = {}
        for layer_name in cells_visual[0].color_layers:
            color_tables[layer_name] = []
            color_layers[layer_name] = bm.loops.layers.color.new(layer_name)

        # Replace this with the correct method to check if a vertex group exists (I didn't find it).
        # Since we will have only a few at most the impact is negligible.
        vertex_groups = {}
        for vg_name in VERTEX_GROUPS:
            for _vg in obj.vertex_groups:
                if _vg.name == vg_name:
                    vertex_groups[vg_name] = _vg
                    break
            if vg_name not in vertex_groups:
                vertex_groups[vg_name] = obj.vertex_groups.new(name=vg_name)

        for cv in cells_visual:
            for layer, color in cv.color_layers.items():
                for f in cv.faces:
                    color_tables[layer].extend([color] * f.corners())

        for layer_name in color_layers:
            color_layer = color_layers[layer_name]
            color_table = color_tables[layer_name]
            for face in bm.faces:
                for loop in face.loops:
                    loop[color_layer] = color_table[loop.vert.index]

        bm.to_mesh(mesh)

        for cv in cells_visual:
            for f in cv.get_faces_with_vertex_weights():
                for vg, weights in f.vertex_groups.items():
                    for ind, weight in enumerate(weights):
                        vertex_groups[vg].add([f.vertices_indexes[ind]], weight, "ADD")