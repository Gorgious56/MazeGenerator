import bpy
from mathutils import Color
from ... maze_logic . algorithms import algorithm_manager
from ... utils . modifier_manager import add_modifier
from ... utils . distance_manager import Distances
from ... utils . vertex_colors_manager import set_vertex_colors
from . grid import Grid


class VisualGrid:
    def __init__(self, scene, props):
        self.obj_walls = None
        self.mesh_walls = None
        self.obj_cells = None
        self.mesh_cells = None
        self.props = props
        self.grid = self.generate_grid()
        self.generate_objects(scene)
        self.generate_modifiers()
        self.offset_grid()

    def generate_grid(self):
        props = self.props
        g = Grid(props.rows_or_radius, props.rows_or_radius)
        algorithm_manager.work(props.maze_algorithm, g, props.seed, max_steps=props.steps)
        g.braid_dead_ends(props.braid_dead_ends)
        return g

    def generate_objects(self, scene):
        # Get or add the Wall mesh
        try:
            self.mesh_wall = bpy.data.meshes['Wall Mesh']
            self.mesh_wall.clear_geometry()
        except KeyError:
            self.mesh_wall = bpy.data.meshes.new("Wall Mesh")

        # Get or add the Wall object and link it to the wall mesh
        try:
            self.obj_walls = scene.objects['Wall']
        except KeyError:
            self.obj_walls = bpy.data.objects.new('Wall', self.mesh_wall)
            scene.collection.objects.link(self.obj_walls)

        # Get or add the Cells mesh
        try:
            self.mesh_cells = bpy.data.meshes['Cells Mesh']
            self.mesh_cells.clear_geometry()
        except KeyError:
            self.mesh_cells = bpy.data.meshes.new("Cells Mesh")

        # Get or add the Wall object and link it to the wall mesh
        try:
            self.obj_cells = scene.objects['Cells']
        except KeyError:
            self.obj_cells = bpy.data.objects.new('Cells', self.mesh_cells)
            scene.collection.objects.link(self.obj_cells)

    def generate_modifiers(self):
        props = self.props
        add_modifier(self.obj_walls, 'WELD', 'Weld')
        add_modifier(self.obj_walls, 'SCREW', 'Screw', properties={'angle': 0, 'steps': 2, 'render_steps': 2, 'screw_offset': props.wall_height, 'use_smooth_shade': False})
        add_modifier(self.obj_walls, 'SOLIDIFY', 'Solidify', properties={'solidify_mode': 'NON_MANIFOLD', 'thickness': props.wall_width, 'offset': 0})

    def offset_grid(self):
        self.obj_walls.location.xyz = self.obj_cells.location.xyz = (-self.grid.columns / 2, -self.grid.rows / 2, 0)
        #  = (-self.grid.columns / 2, -self.grid.rows / 2, 0)

    def build_objects(self):
        all_walls, all_cells = self.grid.get_blueprint()        

        self.mesh_wall.from_pydata(
            all_walls,
            [(i, i + 1) for i in range(0, len(all_walls) - 1, 2)],
            [])

        edges = [(i, i + 1) for i in range(0, len(all_cells) - 1, 4)]
        edges.extend([(j + 1, j + 2) for j in range(0, len(all_cells) - 2, 4)])
        edges.extend([(j + 2, j + 3) for j in range(0, len(all_cells) - 3, 4)])
        edges.extend([(j + 3, j) for j in range(0, len(all_cells) - 4, 4)])

        self.mesh_cells.from_pydata(
            all_cells,
            edges,
            [(j, j + 1, j + 2, j + 3) for j in range(0, len(all_cells) - 3, 4)]
        )

        distances = Distances(self.grid.get_random_unmasked_and_linked_cell(_seed=self.props.seed))
        distances.get_distances()
        new_start, distance = distances.max()
        distances = Distances(new_start)
        distances.get_distances()
        goal, max_distance = distances.max()

        cell_colors = []
        for c in self.grid.get_unmasked_and_linked_cells():
            this_distance = distances[c]
            # Do not simplify "if this_distance is not None" to "if this distance"
            if this_distance is not None:
                relative_distance = this_distance / max_distance
                new_col = Color((relative_distance, 1 - relative_distance, 0))
                new_col.h = (new_col.h + self.props.color_shift) % 1
                cell_colors.append((new_col.r, new_col.g, new_col.b, 1))
            else:
                cell_colors.append((0.5, 0.5, 0.5, 1))

        set_vertex_colors(self.obj_cells, cell_colors, 4)      
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
        
        #  if hasattr(bm.verts, "ensure_lookup_table"):
        #             bm.verts.ensure_lookup_table()
        # bm.to_mesh(mesh_wall)
