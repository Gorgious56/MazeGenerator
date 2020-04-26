import bmesh
import random
from typing import Iterable
from mathutils import Matrix
from ..maze_logic import constants as cell_cst
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

        cells_corners = []
        cells_faces = []
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
        stairs_vg_cells = bm_cells.verts.layers.deform.new()
        stairs_vg_walls = bm_walls.verts.layers.deform.new()

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
                bm_cells_vert[stairs_vg_cells][0] = weights[0]

                bm_walls_vert = bm_walls.verts[v_ind]
                bm_walls_vert[stairs_vg_walls][0] = weights[0]

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

    def on_new_cell(grid, cell):
        MeshManager.verts_indices[cell] = MeshManager.get_verts_indices_from_cell(cell, grid)

    def get_verts_indices_from_cell(cell, grid) -> Iterable[int]:
        row = cell.row
        column = cell.column
        columns = grid.columns
        grid_type = type(grid)
        if grid_type is grids.Grid:
            return (column * 2) + row * columns * 4, (column * 2) + 1 + row * columns * 4, (column * 2) + 1 + row * columns * 4 + columns * 2, (column * 2) + row * columns * 4 + columns * 2
        elif grid_type is grids.GridTriangle:
            b = c = -1
            a = 3 * columns * row + column * 1.5
            if columns % 2 == 0:
                c = a + columns * 1.5
                if cell.is_upright():
                    b = a + 1
                    if column % 2 == 1:
                        a -= 0.5
                        b -= 0.5
                        c += 0.5
                else:
                    b = c + 1
                    if column % 2 == 1:
                        a += 0.5
                        b -= 0.5
                        c -= 0.5
            else:
                if cell.is_upright():
                    if column % 2 == 1:
                        a -= 0.5
                    b = a + 1
                    c = a + columns * 1.5 + 0.5
                else:
                    if column % 2 == 1:
                        a += 0.5
                    b = a + columns * 1.5 + 0.5
                    c = b - 1

            return int(a), int(b), int(c)

    def get_mesh_info(grid):
        columns, rows = grid.columns, grid.rows
        verts = None
        grid_type = type(grid)
        if grid_type is grids.Grid:
            verts = [None] * (4 * columns * rows)
        elif grid_type is grids.GridTriangle:
            verts = [None] * (3 * columns * rows)
        cells_data = {}
        faces = []
        walls_edges = []
        max_distance = grid.distances.max[1]
        longest_path = grid.longest_path
        for c in grid.all_cells:
            verts_indices = MeshManager.verts_indices[c]
            corners = grid.get_cell_positions(c)
            for i in range(len(corners)):
                verts[verts_indices[i]] = corners[i]
            if c.has_any_link():
                faces.append(verts_indices)
                for n in c.get_neighbors_linked_to_me():
                    direction = c.get_neighbor_direction(n)
                    neighbor_indices = MeshManager.verts_indices[n]
                    if grid_type == grids.Grid:
                        if direction == cell_cst.NORTH:
                            faces.append((verts_indices[3], verts_indices[2], neighbor_indices[1], neighbor_indices[0]))
                            walls_edges.append((verts_indices[2], neighbor_indices[1]))
                            walls_edges.append((verts_indices[3], neighbor_indices[0]))
                        elif direction == cell_cst.WEST:
                            faces.append((neighbor_indices[1], verts_indices[0], verts_indices[3], neighbor_indices[2]))
                            walls_edges.append((verts_indices[3], neighbor_indices[2]))
                            walls_edges.append((verts_indices[0], neighbor_indices[1]))
                    elif grid_type == grids.GridTriangle:
                        if c.is_upright():
                            if direction == cell_cst.TRI_UP_LEFT:
                                faces.append((verts_indices[0], verts_indices[2], neighbor_indices[1], neighbor_indices[0]))
                                walls_edges.append((verts_indices[2], neighbor_indices[1]))
                                walls_edges.append((verts_indices[0], neighbor_indices[0]))
                            elif direction == cell_cst.TRI_UP_RIGHT:
                                faces.append((neighbor_indices[0], neighbor_indices[2], verts_indices[2], verts_indices[1]))
                                walls_edges.append((verts_indices[2], neighbor_indices[2]))
                                walls_edges.append((verts_indices[1], neighbor_indices[0]))
                            elif direction == cell_cst.TRI_UP_DOWN:
                                faces.append((neighbor_indices[2], neighbor_indices[1], verts_indices[1], verts_indices[0]))
                                walls_edges.append((verts_indices[1], neighbor_indices[1]))
                                walls_edges.append((verts_indices[0], neighbor_indices[2]))
                this_distance = grid.distances[c]
                cells_data[verts_indices] = ((this_distance / max_distance) if this_distance else 0, 0 if c in longest_path else 1, c.group, len(c.links))
            for direction, w in enumerate(c.get_wall_mask()):
                if w:
                    if grid_type == grids.Grid:
                        if direction == cell_cst.NORTH:
                            walls_edges.append((verts_indices[2], verts_indices[3]))
                        elif direction == cell_cst.WEST:
                            walls_edges.append((verts_indices[3], verts_indices[0]))
                        elif direction == cell_cst.SOUTH:
                            walls_edges.append((verts_indices[0], verts_indices[1]))
                        elif direction == cell_cst.EAST:
                            walls_edges.append((verts_indices[1], verts_indices[2]))
                    elif grid_type == grids.GridTriangle:
                        if c.is_upright():
                            if direction == cell_cst.TRI_UP_LEFT:
                                walls_edges.append((verts_indices[0], verts_indices[2]))
                            elif direction == cell_cst.TRI_UP_RIGHT:
                                walls_edges.append((verts_indices[1], verts_indices[2]))
                            elif direction == cell_cst.TRI_UP_DOWN:
                                walls_edges.append((verts_indices[0], verts_indices[1]))
                        else:
                            if direction == cell_cst.TRI_DN_LEFT:
                                walls_edges.append((verts_indices[0], verts_indices[2]))
                            elif direction == cell_cst.TRI_DN_RIGHT:
                                walls_edges.append((verts_indices[0], verts_indices[1]))
                            elif direction == cell_cst.TRI_DN_UP:
                                walls_edges.append((verts_indices[1], verts_indices[2]))

        return verts, faces, cells_data, walls_edges
