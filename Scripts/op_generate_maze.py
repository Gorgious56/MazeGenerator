from bpy.types import Operator
import bpy
from . maze_logic . data_structure import grid
from . maze_logic . algorithms import algorithm_manager
from . utils . modifier_manager import add_modifier
from . utils . vertex_colors_manager import set_vertex_colors
from . utils . distance_manager import Distances
from time import time
from mathutils import Color

class GenerateMazeOperator(Operator):
    """Tooltip"""
    bl_idname = "maze.generate"
    bl_label = "Generate Maze"

    @classmethod
    def poll(cls, context):
        mg_props = context.scene.mg_props
        return mg_props.rows_or_radius > 0

    def execute(self, context):
        start_time = time()
        self.main(context)
        print(str((time() - start_time) * 1000).split('.')[0] + ' ms')
        return {'FINISHED'}

    def main(self, context):
        scene = context.scene
        mg_props = scene.mg_props
        seed = mg_props.seed

        g = grid.Grid(mg_props.rows_or_radius, mg_props.rows_or_radius)
        algorithm_manager.work(mg_props.maze_algorithm, g, seed, max_steps=mg_props.steps)
        g.braid_dead_ends(mg_props.braid_dead_ends)

        # Get or add the Wall mesh
        try:
            mesh_wall = bpy.data.meshes['Wall Mesh']
            mesh_wall.clear_geometry()
        except KeyError:
            mesh_wall = bpy.data.meshes.new("Wall Mesh")

        # Get or add the Wall object and link it to the wall mesh
        try:
            obj_wall = scene.objects['Wall']
        except KeyError:
            obj_wall = bpy.data.objects.new('Wall', mesh_wall)
            scene.collection.objects.link(obj_wall)

        add_modifier(obj_wall, 'WELD', 'Weld')
        add_modifier(obj_wall, 'SCREW', 'Screw')
        obj_wall.modifiers['Screw'].angle = 0
        obj_wall.modifiers['Screw'].steps = 2
        obj_wall.modifiers['Screw'].render_steps = 2
        obj_wall.modifiers['Screw'].screw_offset = mg_props.wall_height
        obj_wall.modifiers["Screw"].use_smooth_shade = False
        add_modifier(obj_wall, 'SOLIDIFY', 'Solidify')
        obj_wall.modifiers["Solidify"].solidify_mode = 'NON_MANIFOLD'
        obj_wall.modifiers["Solidify"].thickness = mg_props.wall_width
        obj_wall.modifiers["Solidify"].offset = 0

        try:
            mesh_cells = bpy.data.meshes['Cells Mesh']
            mesh_cells.clear_geometry()
        except KeyError:
            mesh_cells = bpy.data.meshes.new("Cells Mesh")

        # Get or add the Wall object and link it to the wall mesh
        try:
            obj_cells = scene.objects['Cells']
        except KeyError:
            obj_cells = bpy.data.objects.new('Cells', mesh_cells)
            scene.collection.objects.link(obj_cells)

        obj_wall.location.xyz = (-g.columns / 2, -g.rows / 2, 0)
        obj_cells.location.xyz = (-g.columns / 2, -g.rows / 2, 0)

        all_walls, all_cells = g.get_blueprint()

        mesh_wall.from_pydata(
            all_walls,
            [(i, i + 1) for i in range(0, len(all_walls) - 1, 2)],
            [])

        edges = [(i, i + 1) for i in range(0, len(all_cells) - 1, 4)]
        edges.extend([(j + 1, j + 2) for j in range(0, len(all_cells) - 2, 4)])
        edges.extend([(j + 2, j + 3) for j in range(0, len(all_cells) - 3, 4)])
        edges.extend([(j + 3, j) for j in range(0, len(all_cells) - 4, 4)])

        mesh_cells.from_pydata(
            all_cells,
            edges,
            [(j, j + 1, j + 2, j + 3) for j in range(0, len(all_cells) - 3, 4)]
        )

        distances = Distances(g.get_random_unmasked_and_linked_cell(_seed=seed))
        distances.get_distances()
        new_start, distance = distances.max()
        distances = Distances(new_start)
        distances.get_distances()
        goal, max_distance = distances.max()

        cell_colors = []
        for c in g.get_unmasked_and_linked_cells():
            this_distance = distances[c]
            # Do not simplify "if this_distance is not None" to "if this distance"
            if this_distance is not None:
                relative_distance = this_distance / max_distance
                new_col = Color((relative_distance, 1 - relative_distance, 0))
                new_col.h = (new_col.h + mg_props.color_shift) % 1
                cell_colors.append((new_col.r, new_col.g, new_col.b, 1))
            else:
                cell_colors.append((0.5, 0.5, 0.5, 1))

        set_vertex_colors(obj_cells, cell_colors, 4)

        # bm = bmesh.new()

        # sqrt2over2 = (2**0.5) / 2

        # for i in range(0, len(all_walls) - 1, 2):
        #     wall_start = bm.verts.new(all_walls[i])
        #     wall_end = bm.verts.new(all_walls[i + 1])
        #     bm.edges.new((wall_start, wall_end))

        # for c in g.each_cell():
        #     if not c.exists_and_is_linked_neighbor_index(0):
        #         wall_start = cell_positions[1]
        #         wall_start = cell_positions[2]
        #     new_verts = []
        #     walls, indices = g.get_cell_walls(c)
        #     for wall in walls:
        #         new_verts.append(wall)
        #     for edge in indices:
        #         bm.edges.new(new_verts[edge[0]], new_verts[edge[1]])


        # for v in g.get_wall
        # for c in g.each_cell():
        #     bmesh.ops.create_circle(
        #         bm,
        #         cap_ends=True,    # Fill with faces
        #         radius=sqrt2over2*.9,
        #         segments=4,
        #         matrix=g.get_matrix(c)
        #     )
        


# if hasattr(bm.verts, "ensure_lookup_table"): 
#             bm.verts.ensure_lookup_table()  
        # bm.to_mesh(mesh_wall)
