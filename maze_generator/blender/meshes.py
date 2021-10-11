"""
Contains definitions and methods to store and access Meshes
"""

import bpy
import bmesh
import random
from mathutils import Matrix


class MeshesPropertyGroup(bpy.types.PropertyGroup):
    """
    Stores the meshes used in the add-on
    """

    walls: bpy.props.PointerProperty(name="Wall Mesh", type=bpy.types.Mesh)
    cells: bpy.props.PointerProperty(name="Cells Mesh", type=bpy.types.Mesh)
    
    use_smooth: bpy.props.BoolProperty(
        name="Smooth Shade Meshes",
        description="Enforce smooth shading everytime the maze is generated",
        default=False,
        update=lambda self, context: MeshManager.update_smooth(self),
    )


DISTANCE = "DISTANCE"
GROUP = "GROUP"
UNIFORM = "UNIFORM"
NEIGHBORS = "NEIGHBORS"

DEFAULT_CELL_VISUAL_TYPE = DISTANCE


def generate_cell_visual_enum():
    return [
        (DISTANCE, "Distance", ""),
        (GROUP, "Cell Group", ""),
        (UNIFORM, "Uniform", ""),
        (NEIGHBORS, "Neighbors Amount", ""),
    ]


VG_DISPLACE, VG_STAIRS, VG_THICKNESS, VG_LONGEST_PATH = (
    "MG_DISPLACE",
    "MG_STAIRS",
    "MG_CELL_THICKNESS",
    "MG_LONGEST_PATH",
)

VERTEX_GROUPS = VG_STAIRS, VG_THICKNESS, VG_LONGEST_PATH


class MeshManager:
    # cells = 0

    @staticmethod
    def create_vertex_groups(objects):
        # Replace this with the correct method to check if a vertex group exists
        for vg_name in VERTEX_GROUPS:
            for obj in (objects.cells, objects.walls):
                vg_exists = False
                for _vg in obj.vertex_groups:
                    if _vg.name == vg_name:
                        vg_exists = True
                        break
                if not vg_exists:
                    obj.vertex_groups.new(name=vg_name)

    @staticmethod
    def build_objects(props, grid) -> None:
        mesh_cells = props.objects.cells.data
        mesh_walls = props.objects.walls.data

        cells_corners, cells_faces, stairs_vertex_group, walls_edges = MeshManager.get_mesh_info(
            grid, props.cell_props.inset, props.path.force_outside
        )

        mesh_cells.clear_geometry()
        mesh_cells.from_pydata(cells_corners, [], cells_faces)
        mesh_walls.clear_geometry()
        mesh_walls.from_pydata(cells_corners, walls_edges, [])

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

        vg_stairs_index = VERTEX_GROUPS.index(VG_STAIRS)
        vg_longest_path_index = VERTEX_GROUPS.index(VG_LONGEST_PATH)
        vg_thickness_index = VERTEX_GROUPS.index(VG_THICKNESS)
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

        if (
            props.meshes.use_smooth
        ):  # Update only when the mesh is supposed to be smoothed, because the default will be unsmoothed
            MeshManager.update_smooth(props)
        for mesh in (mesh_cells, mesh_walls):
            mesh.use_auto_smooth = True
            mesh.auto_smooth_angle = 0.5

    @staticmethod
    def update_smooth(props) -> None:
        "Set all mesh objects polygons smooth (or not) according to the props Smooth property"
        smooth = props.meshes.use_smooth
        for mesh in (props.meshes.cells, props.meshes.walls):
            mesh.polygons.foreach_set("use_smooth", [smooth] * len(mesh.polygons))
            mesh.update()

    @staticmethod
    def get_mesh_info(grid, inset, force_outside):
        all_cells = grid.all_cells
        verts = grid.verts

        ranges_info = []
        faces = []
        walls_edges = []
        max_distance = grid.distances.max[1]
        longest_path = grid.longest_path

        exit_cells = (getattr(grid, "start_cell", -1), getattr(grid, "end_cell", -1))

        for c in all_cells:
            verts_indices = range(c.first_vert_index, c.first_vert_index + c.corners)

            faces.append(verts_indices)
            this_distance = grid.distances[c]
            ranges_info.append(
                VerticesRangeInfo(
                    _range=verts_indices,
                    relative_distance=(this_distance / max_distance) if this_distance else -1,
                    is_longest_path=0 if c in longest_path else 1,
                    # TODO : use pointer to cell if not other info is required :
                    cell_group=c.group,
                    links=len(c.links),
                )
            )
            half_neighbors = c.half_neighbors
            for direction, w in enumerate(c.get_wall_mask()):
                if w and direction < len(verts_indices):
                    if c in exit_cells and not c.get_neighbor_towards(direction):
                        continue
                    walls_edges.append((verts_indices[direction], verts_indices[(direction + 1) % c.corners]))
                elif not w and direction in half_neighbors:
                    n = c.get_neighbor_towards(direction)
                    if not n:
                        continue
                    neighbor_indices = range(n.first_vert_index, n.first_vert_index + n.corners)
                    first_idx = direction
                    second_idx = c.get_neighbor_return(direction)

                    faces.append(
                        (
                            verts_indices[first_idx],
                            neighbor_indices[(second_idx + 1) % n.corners],
                            neighbor_indices[second_idx],
                            verts_indices[(first_idx + 1) % c.corners],
                        )
                    )
                    if not inset:
                        continue
                    walls_edges.append((verts_indices[first_idx], neighbor_indices[(second_idx + 1) % n.corners]))
                    walls_edges.append((verts_indices[(first_idx + 1) % c.corners], neighbor_indices[second_idx]))

        return verts, faces, ranges_info, walls_edges


class VerticesRangeInfo:
    def __init__(self, _range, relative_distance, is_longest_path, cell_group, links) -> None:
        self.range = _range
        self.relative_distance = relative_distance
        self.is_longest_path = is_longest_path
        self.cell_group = cell_group
        self.links = links
