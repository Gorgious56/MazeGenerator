"""
Contains definitions and methods to store and access Meshes
"""

import bmesh
import random
from mathutils import Matrix, Vector
from maze_generator.blender.mesh.constants import (
    DISTANCE,
    NEIGHBORS,
    GROUP,
)
from maze_generator.blender.mesh.prop import VerticesRangeInfo
from maze_generator.blender.mesh.vertex_groups.helper import get_vertex_group_index


def build_objects(props, preferences, grid):
    mesh_cells = props.objects.cells.data
    mesh_walls = props.objects.walls.data

    cells_corners, cells_faces, stairs_vertex_group, walls_edges = get_mesh_info(
        grid, props.cell_props.inset, props.path.force_outside
    )

    mesh_cells.clear_geometry()
    mesh_cells.from_pydata(cells_corners, [], cells_faces)
    mesh_walls.clear_geometry()
    mesh_walls.from_pydata(cells_corners, walls_edges, [])
    return
    bm_cells = bmesh.new()
    bm_cells.from_mesh(mesh_cells)

    bm_walls = bmesh.new()
    bm_walls.from_mesh(mesh_walls)

    distance_vc = bm_cells.loops.layers.color.new(DISTANCE)
    group_vc = bm_cells.loops.layers.color.new(GROUP)
    neighbors_vc = bm_cells.loops.layers.color.new(NEIGHBORS)
    vg_cells = bm_cells.verts.layers.deform.new()
    vg_walls = bm_walls.verts.layers.deform.new()

    random.seed(props.display.seed_color)

    groups = grid.groups
    group_colors = {}
    max_groups = max(max(grid.groups), 1)
    for g in groups:
        val = g / max_groups
        group_colors[g] = val, val, val, 1

    max_neighbors = max(grid.max_links_per_cell, 1)
    neighbors_colors = {}
    for n in range(max_neighbors + 1):
        val = n / max_neighbors
        neighbors_colors[n] = val, val, val, 1

    bm_cells.verts.ensure_lookup_table()
    bm_walls.verts.ensure_lookup_table()

    vg_props = preferences.vertex_groups_names
    vg_stairs_index = get_vertex_group_index(props.objects.cells, vg_props.stairs_name)
    vg_longest_path_index = get_vertex_group_index(props.objects.cells, vg_props.longest_path_name)
    vg_thickness_index = get_vertex_group_index(props.objects.cells, vg_props.cell_thickness_name)
    for verts_range in stairs_vertex_group:
        _range = verts_range.range
        relative_distance = verts_range.relative_distance
        is_longest_path = verts_range.is_longest_path
        cell_group = verts_range.cell_group
        links = verts_range.links

        for v_ind in _range:
            bm_cells_vert = bm_cells.verts[v_ind]
            bm_cells_vert[vg_cells][vg_stairs_index] = relative_distance
            bm_cells_vert[vg_cells][vg_longest_path_index] = is_longest_path

            bm_walls_vert = bm_walls.verts[v_ind]
            bm_walls_vert[vg_walls][vg_stairs_index] = relative_distance
            bm_walls_vert[vg_walls][vg_thickness_index] = 1
            bm_walls_vert[vg_walls][vg_longest_path_index] = is_longest_path

            for loop in bm_cells_vert.link_loops:
                loop[distance_vc] = (relative_distance, is_longest_path, 0, 0)
                loop[group_vc] = group_colors[cell_group]
                loop[neighbors_vc] = neighbors_colors[links]

    bm_cells.to_mesh(mesh_cells)
    bm_walls.to_mesh(mesh_walls)

    mesh_cells.transform(Matrix.Translation(grid.offset))
    mesh_walls.transform(Matrix.Translation(grid.offset))

    if props.meshes.use_smooth:  # Update only when the mesh is supposed to be smoothed, default will be unsmoothed
        props.meshes.update_smooth()
    for mesh in (mesh_cells, mesh_walls):
        mesh.use_auto_smooth = True
        mesh.auto_smooth_angle = 0.5


def get_mesh_info(grid, inset, force_outside):
    verts = []
    offset = 0

    ranges_info = []
    faces = []
    walls_edges = []
    # max_distance = grid.distances.max[1]
    longest_path = grid.longest_path

    exit_cells = (getattr(grid, "start_cell", -1), getattr(grid, "end_cell", -1))
    verts_indices = []

    neighbors_return = (2, 3, 0, 1)
    half_neighbors = grid.half_neighbors
    for c_idx, cell in enumerate(grid.cells_np):
        if cell.sum() == 0:
            verts_indices.append(None)
            offset += grid.corners
            continue

        verts.extend(grid.get_cell_info(c_idx))
        first_index = c_idx * 4 - offset
        verts_indices.append(range(first_index, first_index + 4))
        faces.append(verts_indices[-1])
        # faces.append(verts_indices)
        # this_distance = grid.distances[c]
        # ranges_info.append(
        #     VerticesRangeInfo(
        #         _range=verts_indices,
        #         relative_distance=(this_distance / max_distance) if this_distance else -1,
        #         is_longest_path=0 if c in longest_path else 1,
        #         # TODO : use pointer to cell if no other info is required :
        #         cell_group=c.group,
        #         links=len(c.links),
        #     )
        # )

    for c_idx, cell in enumerate(grid.cells_np):
        current_verts_indices = verts_indices[c_idx]
        if current_verts_indices is None:
            continue
        for direction, link in enumerate(grid.cells_np[c_idx]):
            if not link and direction < len(current_verts_indices):
                if c_idx in exit_cells and not c_idx.get_neighbor_towards(direction):
                    continue
                walls_edges.append(
                    (current_verts_indices[direction], current_verts_indices[(direction + 1) % grid.corners])
                )
            elif link and direction in half_neighbors:
                n = grid.get_neighbor_towards(c_idx, direction)
                if not n:
                    continue
                neighbor_indices = verts_indices[n]
                first_idx = direction
                second_idx = neighbors_return[direction]
                # second_idx = grid.get_neighbor_return(c_idx, direction)

                faces.append(
                    (
                        current_verts_indices[first_idx],
                        neighbor_indices[(second_idx + 1) % grid.corners],
                        neighbor_indices[second_idx],
                        current_verts_indices[(first_idx + 1) % grid.corners],
                    )
                )
                if not inset:
                    continue
                walls_edges.append((current_verts_indices[first_idx], neighbor_indices[(second_idx + 1) % grid.corners]))
                walls_edges.append((current_verts_indices[(first_idx + 1) % grid.corners], neighbor_indices[second_idx]))

    return verts, faces, ranges_info, walls_edges
