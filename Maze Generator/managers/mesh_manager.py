import bmesh
from ..visual.cell_visual import VERTEX_GROUPS


class MeshManager:
    vertex_groups_cells = {}
    vertex_group_walls = {}

    def remove_all_vertex_layers(mesh):
        vertex_colors = mesh.vertex_colors
        while vertex_colors:
            vertex_colors.remove(vertex_colors[0])

    def create_vertex_groups(cells, walls):
        # Replace this with the correct method to check if a vertex group exists (I didn't find it).
        # Since we will have only a few at most the impact is negligible.
        for vg_name in VERTEX_GROUPS:
            for obj, vertex_groups in zip((cells, walls), (MeshManager.vertex_groups_cells, MeshManager.vertex_group_walls)):
                for _vg in obj.vertex_groups:
                    if _vg.name == vg_name:
                        vertex_groups[vg_name] = _vg
                        break
                if vg_name not in vertex_groups:
                    vertex_groups[vg_name] = obj.vertex_groups.new(name=vg_name)

    def set_mesh_layers(obj_cells, obj_walls, cells_visual, props):
        if cells_visual:
            mesh_walls = obj_walls.data
            MeshManager.remove_all_vertex_layers(mesh_walls)

            bm_walls = bmesh.new()
            bm_walls.from_mesh(mesh_walls)

            mesh_cells = obj_cells.data
            MeshManager.remove_all_vertex_layers(mesh_cells)

            bm_cells = bmesh.new()
            bm_cells.from_mesh(mesh_cells)

            color_tables = {}
            color_layers = {}
            for layer_name in cells_visual[0].color_layers:
                color_tables[layer_name] = []
                color_layers[layer_name] = bm_cells.loops.layers.color.new(layer_name)

            MeshManager.create_vertex_groups(obj_cells, obj_walls)

            for cv in cells_visual:
                for layer, color in cv.color_layers.items():
                    for f in cv.faces:
                        color_tables[layer].extend([color] * f.corners())

            for layer_name in color_layers:
                color_layer = color_layers[layer_name]
                color_table = color_tables[layer_name]
                for face in bm_cells.faces:
                    for loop in face.loops:
                        loop[color_layer] = color_table[loop.vert.index]

            bm_cells.to_mesh(mesh_cells)

            for cv in cells_visual:
                for f in cv.get_faces_with_vertex_weights():
                    for vg, weights in f.vertex_groups.items():
                        for ind, weight in enumerate(weights):
                            MeshManager.vertex_groups_cells[vg].add([f.vertices_indices[ind]], weight, "ADD")
                    for vg, weights in f.walls_vertex_groups.items():
                        for ind, weight in enumerate(weights):
                            MeshManager.vertex_group_walls[vg].add([f.walls_indices[ind]], weight, 'ADD')

            # if props.cell_inset > 0:
            #     bm_cells = bmesh.new()
            #     bm_cells.from_mesh(mesh_cells)
            #     bmesh.ops.remove_doubles(bm_cells, verts=bm_cells.verts, dist=0.000001)
            #     bm_cells.to_mesh(mesh_cells)
