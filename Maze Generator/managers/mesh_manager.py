import bmesh
import random
from typing import Iterable
from mathutils import Matrix
from ..maze_logic import grids


DISTANCE = 'DISTANCE'
GROUP = 'GROUP'
UNIFORM = 'UNIFORM'
NEIGHBORS = 'NEIGHBORS'

DEFAULT_CELL_VISUAL_TYPE = DISTANCE


def generate_cell_visual_enum():
    return [(DISTANCE, 'Distance', ''),
            (GROUP, 'Cell Group', ''),
            (UNIFORM, 'Uniform', ''),
            (NEIGHBORS, 'Neighbors Amount', ''),
            ]


VG_DISPLACE, VG_STAIRS, VG_THICKNESS = 'MG_DISPLACE', 'MG_STAIRS', 'MG_CELL_THICKNESS'

VERTEX_GROUPS = VG_STAIRS, VG_THICKNESS


class MeshManager:
    vertex_groups_cells = {}
    vertex_group_walls = {}
    verts_indices = {}
    cells = 0

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

    def build_objects(props, grid, obj_cells, obj_walls) -> None:
        mesh_cells = obj_cells.data
        mesh_walls = obj_walls.data

        cells_corners, cells_faces, stairs_vertex_group, walls_edges = MeshManager.get_mesh_info(grid)

        mesh_cells.clear_geometry()
        mesh_cells.from_pydata(
            cells_corners,
            [],
            cells_faces
        )
        mesh_walls.clear_geometry()
        mesh_walls.from_pydata(
            cells_corners,
            walls_edges,
            [])

        bm_cells = bmesh.new()
        bm_cells.from_mesh(mesh_cells)

        bm_walls = bmesh.new()
        bm_walls.from_mesh(mesh_walls)

        distance_vc = bm_cells.loops.layers.color.new(DISTANCE)
        group_vc = bm_cells.loops.layers.color.new(GROUP)
        neighbors_vc = bm_cells.loops.layers.color.new(NEIGHBORS)
        vg_cells = bm_cells.verts.layers.deform.new()
        vg_walls = bm_walls.verts.layers.deform.new()

        random.seed(props.seed_color)

        rand = random.random
        groups = []
        group_colors = {}
        for c in grid.get_linked_cells():
            if c.group not in groups:
                groups.append(c.group)
        for g in groups:
            group_colors[g] = rand(), rand(), rand(), 1

        neighbors_colors = {}
        for n in [i for i in range(10)]:
            neighbors_colors[n] = (rand(), rand(), rand(), 1)

        bm_cells.verts.ensure_lookup_table()
        bm_walls.verts.ensure_lookup_table()
        for vg_info, weights in stairs_vertex_group.items():
            for v_ind in vg_info:
                bm_cells_vert = bm_cells.verts[v_ind]
                bm_cells_vert[vg_cells][0] = weights[0]

                bm_walls_vert = bm_walls.verts[v_ind]
                bm_walls_vert[vg_walls][0] = weights[0]
                bm_walls_vert[vg_walls][1] = 1

                for loop in bm_cells_vert.link_loops:
                    loop[distance_vc] = (weights[0], weights[1], 0, 0)
                    loop[group_vc] = group_colors[weights[2]]
                    loop[neighbors_vc] = neighbors_colors[weights[3]]

        bm_cells.to_mesh(mesh_cells)
        bm_walls.to_mesh(mesh_walls)

        mesh_cells.transform(Matrix.Translation(grid.offset))
        mesh_walls.transform(Matrix.Translation(grid.offset))

        if props.cell_use_smooth:  # Update only when the mesh is supposed to be smoothed, because the default will be unsmoothed
            MeshManager.update_smooth(props, mesh_cells, mesh_walls)
        for mesh in (mesh_cells, mesh_walls):
            mesh.use_auto_smooth = True
            mesh.auto_smooth_angle = 0.5

    def update_smooth(props, mesh_cells, mesh_walls) -> None:
        smooth = props.cell_use_smooth
        for p in mesh_cells.polygons:
            p.use_smooth = smooth
        for p in mesh_walls.polygons:
            p.use_smooth = smooth

    def reset():
        MeshManager.verts_indices = {}
        MeshManager.cells = 0

    def on_new_cell(grid, cell):
        MeshManager.verts_indices[cell] = range(MeshManager.cells, MeshManager.cells + grid.CELL_SIDES)
        MeshManager.cells += grid.CELL_SIDES

    def get_mesh_info(grid):
        all_cells = grid.all_cells
        verts = [None] * MeshManager.cells

        cells_data = {}
        faces = []
        walls_edges = []
        max_distance = grid.distances.max[1]
        longest_path = grid.longest_path
        for c in all_cells:
            verts_indices = MeshManager.verts_indices[c]
            corners = grid.get_cell_positions(c)
            for i in range(len(corners)):
                verts[verts_indices[i]] = corners[i]
            if c.has_any_link():
                faces.append(verts_indices)
                this_distance = grid.distances[c]
                cells_data[verts_indices] = ((this_distance / max_distance) if this_distance else 0, 0 if c in longest_path else 1, c.group, len(c.links))
            half_neighbors = c.get_half_neighbors()
            for direction, w in enumerate(c.get_wall_mask()):
                if w and direction < len(verts_indices):
                    walls_edges.append((verts_indices[direction], verts_indices[(direction + 1) % grid.CELL_SIDES]))
                elif not w and direction in half_neighbors:
                    n = c.get_neighbor_towards(direction)
                    if n:
                        neighbor_indices = MeshManager.verts_indices[n]
                        first_idx = direction
                        second_idx = c.get_neighbor_return(direction)

                        faces.append((verts_indices[first_idx], neighbor_indices[(second_idx + 1) % grid.CELL_SIDES], neighbor_indices[second_idx], verts_indices[(first_idx + 1) % grid.CELL_SIDES]))
                        walls_edges.append((verts_indices[first_idx], neighbor_indices[(second_idx + 1) % grid.CELL_SIDES]))
                        walls_edges.append((verts_indices[(first_idx + 1) % grid.CELL_SIDES], neighbor_indices[second_idx]))

        return verts, faces, cells_data, walls_edges
