import bpy
from random import seed, random
from .. utils . modifier_manager import add_modifier, add_driver_to, WALL_BEVEL_NAME, WALL_WELD_NAME, WALL_SCREW_NAME, WALL_SOLIDIFY_NAME, CELL_SOLIDIFY_NAME, \
    CELL_WELD_NAME, CELL_DECIMATE_NAME, CELL_BEVEL_NAME, CELL_SUBSURF_NAME, CELL_DISPLACE_NAME, CELL_WELD_2_NAME
from .. utils . distance_manager import Distances
from .. utils . mesh_manager import set_mesh_layers
from .. utils . material_manager import MaterialManager
from .. maze_logic . data_structure . grids . grid import Grid
from .. maze_logic . data_structure . grids . grid_polar import GridPolar
from .. maze_logic . data_structure . grids . grid_hex import GridHex
from .. maze_logic . data_structure . grids . grid_triangle import GridTriangle
from .. maze_logic . data_structure . grids . grid_weave import GridWeave
from .. maze_logic . data_structure . cell import CellUnder
from .. maze_logic import algorithm_manager
from .. visual . cell_type_manager import POLAR, TRIANGLE, HEXAGON, get_cell_vertices
from .. visual . cell_visual_manager import DISTANCE, GROUP, NEIGHBORS, DISPLACE


class MazeVisual:
    Instance = None
    mat_mgr = None

    def __init__(self, scene):
        self.obj_walls = None
        self.mesh_walls = None
        self.obj_cells = None
        self.mesh_cells = None
        self.grid = None

        self.scene = scene
        self.props = scene.mg_props
        props = self.props

        self.cell_vertices = get_cell_vertices(self.props.cell_type)
        self.cells_vertices = []
        self.cells_visual = []

        self.generate_grid()
        algorithm_manager.work(props.maze_algorithm, self.grid, props.seed, max_steps=props.steps, bias=props.maze_bias)
        self.grid.sparse_dead_ends(props.sparse_dead_ends, props.braid_dead_ends, props.seed)
        props.dead_ends = self.grid.braid_dead_ends(props.braid_dead_ends, props.seed)

        self.generate_objects()
        self.build_objects()
        self.generate_modifiers()
        self.generate_drivers()

        if MazeVisual.mat_mgr is None:
            MazeVisual.mat_mgr = MaterialManager(self)
        else:
            MazeVisual.mat_mgr.update(self)
        self.set_materials()

        self.paint_cells()
        self.offset_objects()
        self.update_visibility()

        MazeVisual.Instance = self

    def update_visibility(self):
        set_hidden = self.props.wall_hide and self.props.cell_inset > 0 or self.props.maze_weave
        self.obj_walls.hide_viewport = bool(set_hidden)
        self.obj_walls.hide_render = bool(set_hidden)

    def generate_grid(self):
        props = self.props
        grid = None
        if props.cell_type == POLAR:
            grid = GridPolar
        elif props.cell_type == HEXAGON:
            grid = GridHex
        elif props.cell_type == TRIANGLE:
            grid = GridTriangle
        else:
            if props.maze_weave:
                self.grid = GridWeave(
                    rows=props.rows_or_radius,
                    columns=props.rows_or_radius,
                    cell_size=1 - max(0.1, props.cell_inset),
                    use_kruskal=props.maze_algorithm == algorithm_manager.ALGO_KRUSKAL_RANDOM,
                    weave=props.maze_weave)
                return
            else:
                grid = Grid
        g = grid(rows=props.rows_or_radius, columns=props.rows_or_radius, cell_size=1 - props.cell_inset)
        self.grid = g

    def generate_objects(self):
        scene = self.scene
        # Get or add the Wall mesh
        try:
            self.mesh_wall = bpy.data.meshes['Wall Mesh']
            self.mesh_wall.clear_geometry()
        except KeyError:
            self.mesh_wall = bpy.data.meshes.new("Wall Mesh")

        # Get or add the Wall object and link it to the wall mesh
        try:
            self.obj_walls = scene.objects['Walls']
        except KeyError:
            self.obj_walls = bpy.data.objects.new('Walls', self.mesh_wall)
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
        if props.auto_overwrite:
            self.obj_walls.modifiers.clear()
        add_modifier(self.obj_walls, 'WELD', WALL_WELD_NAME, properties={'show_expanded': False})
        add_modifier(self.obj_walls, 'SCREW', WALL_SCREW_NAME, properties={'show_expanded': False, 'angle': 0, 'steps': 2, 'render_steps': 2, 'screw_offset': props.wall_height})
        add_modifier(self.obj_walls, 'SOLIDIFY', WALL_SOLIDIFY_NAME, properties={'show_expanded': False, 'solidify_mode': 'NON_MANIFOLD', 'thickness': props.wall_width, 'offset': 0})
        add_modifier(self.obj_walls, 'BEVEL', WALL_BEVEL_NAME, properties={'show_expanded': False, 'segments': 4, 'limit_method': 'ANGLE'})

        if props.auto_overwrite:
            self.obj_cells.modifiers.clear()
        add_modifier(self.obj_cells, 'WELD', CELL_WELD_NAME, properties={'show_expanded': False, 'vertex_group': DISPLACE, 'invert_vertex_group': True})
        add_modifier(self.obj_cells, 'WELD', CELL_WELD_2_NAME, properties={'show_expanded': False, 'vertex_group': DISPLACE, 'invert_vertex_group': False})
        add_modifier(self.obj_cells, 'SOLIDIFY', CELL_SOLIDIFY_NAME, properties={'show_expanded': False, 'use_even_offset': True, 'vertex_group': DISPLACE, 'invert_vertex_group': True})
        # add_modifier(self.obj_cells, 'DECIMATE', CELL_DECIMATE_NAME, properties={'show_expanded': False, 'decimate_type': 'DISSOLVE'})
        add_modifier(self.obj_cells, 'BEVEL', CELL_BEVEL_NAME, properties={'show_expanded': False, 'segments': 2, 'limit_method': 'ANGLE', 'material': 1, 'profile': 1, 'angle_limit': 1.5, 'use_clamp_overlap': False})
        add_modifier(self.obj_cells, 'SUBSURF', CELL_SUBSURF_NAME, properties={'show_expanded': False})
        add_modifier(self.obj_cells, 'DISPLACE', CELL_DISPLACE_NAME, properties={'show_expanded': False, 'direction': 'Z', 'vertex_group': DISPLACE, 'mid_level': 0})

    def set_materials(self):
        if MazeVisual.mat_mgr:
            MazeVisual.mat_mgr.set_materials()

    def generate_drivers(self):
        add_driver_to(self.obj_walls.modifiers[WALL_SCREW_NAME], 'screw_offset', 'wall_height', 'SCENE', self.scene, 'mg_props.wall_height')
        add_driver_to(self.obj_walls.modifiers[WALL_SCREW_NAME], 'use_smooth_shade', 'wall_bevel', 'SCENE', self.scene, 'mg_props.wall_bevel', expression='wall_bevel > .005')
        add_driver_to(self.obj_walls.modifiers[WALL_SOLIDIFY_NAME], 'thickness', 'wall_thickness', 'SCENE', self.scene, 'mg_props.wall_width')
        add_driver_to(self.obj_walls.modifiers[WALL_BEVEL_NAME], 'width', 'wall_bevel', 'SCENE', self.scene, 'mg_props.wall_bevel')

        add_driver_to(self.obj_cells.modifiers[CELL_SOLIDIFY_NAME], 'thickness', 'cell_thickness', 'SCENE', self.scene, 'mg_props.cell_thickness')
        add_driver_to(self.obj_cells.modifiers[CELL_SOLIDIFY_NAME], 'thickness_vertex_group', 'cell_thickness', 'SCENE', self.scene, 'mg_props.cell_thickness', expression='max(0, 1 - abs(cell_thickness / 2))')
        add_driver_to(self.obj_cells.modifiers[CELL_BEVEL_NAME], 'width', 'cell_contour', 'SCENE', self.scene, 'mg_props.cell_contour')
        # add_driver_to(self.obj_cells.modifiers[CELL_DECIMATE_NAME], 'show_viewport', 'cell_inset', 'SCENE', self.scene, 'mg_props.cell_inset', expression='cell_inset > 0')
        # add_driver_to(self.obj_cells.modifiers[CELL_DECIMATE_NAME], 'show_render', 'cell_inset', 'SCENE', self.scene, 'mg_props.cell_inset', expression='cell_inset > 0')
        add_driver_to(self.obj_cells.modifiers[CELL_SUBSURF_NAME], 'levels', 'cell_subdiv', 'SCENE', self.scene, 'mg_props.cell_subdiv')
        add_driver_to(self.obj_cells.modifiers[CELL_SUBSURF_NAME], 'render_levels', 'cell_subdiv', 'SCENE', self.scene, 'mg_props.cell_subdiv')
        add_driver_to(self.obj_cells.modifiers[CELL_DISPLACE_NAME], 'strength', 'cell_thickness', 'SCENE', self.scene, 'mg_props.cell_thickness', expression='- (cell_thickness + (abs(cell_thickness) / cell_thickness * 0.1)) if cell_thickness != 0 else 0')
        add_driver_to(self.obj_cells.modifiers[CELL_DISPLACE_NAME], 'show_viewport', 'cell_thickness', 'SCENE', self.scene, 'mg_props.cell_thickness', expression='cell_thickness != 0')
        add_driver_to(self.obj_cells.modifiers[CELL_DISPLACE_NAME], 'show_render', 'cell_thickness', 'SCENE', self.scene, 'mg_props.cell_thickness', expression='cell_thickness != 0')

    def offset_objects(self):
        if self.props.cell_type == POLAR:
            self.obj_walls.location.xyz = self.obj_cells.location.xyz = (0, 0, 0)
        elif self.props.cell_type == TRIANGLE:
            self.obj_walls.location.xyz = self.obj_cells.location.xyz = (-self.grid.columns / 4, -self.grid.rows / 2 + 0.5, 0)
        else:
            self.obj_walls.location.xyz = self.obj_cells.location.xyz = (-self.grid.columns / 2, -self.grid.rows / 2, 0)

    def build_objects(self):
        self.cells_visual = self.grid.get_blueprint()

        all_walls = []
        for cv in self.cells_visual:
            all_walls.extend(cv.walls)

        self.mesh_wall.from_pydata(
            all_walls,
            [(i, i + 1) for i in range(0, len(all_walls) - 1, 2)],
            [])

        cells_corners = []
        cells_edges = []
        cells_faces = []
        vertices = 0
        for cv in self.cells_visual:
            for f in cv.faces:
                f.translate(vertices)
                cells_corners.extend(f.vertices)
                cells_edges.extend(f.edges)
                cells_faces.append(f.face)
                vertices += f.corners()

        self.mesh_cells.from_pydata(
            cells_corners,
            cells_edges,
            cells_faces
        )

        if self.props.cell_use_smooth:  # Update only when the mesh is supposed to be smoothed, because the default will be unsmoothed
            self.update_cell_smooth()
        self.mesh_cells.use_auto_smooth = True
        self.mesh_cells.auto_smooth_angle = 0.5

    def update_cell_smooth(self):
        smooth = self.props.cell_use_smooth
        for p in self.mesh_cells.polygons:
            p.use_smooth = smooth

    def paint_cells(self):
        unmasked_and_linked_cells = self.grid.get_unmasked_and_linked_cells()

        distances = Distances(self.grid.get_random_unmasked_and_linked_cell(_seed=self.props.seed))
        distances.get_distances()
        new_start, distance = distances.max()
        distances = Distances(new_start)
        distances.get_distances()
        goal, max_distance = distances.max()

        longest_path = distances.path_to(goal).path

        seed(self.props.seed_color)

        groups = set()
        group_colors = {}
        for c in unmasked_and_linked_cells:
            groups.add(c.group)
        for g in groups:
            group_colors[g] = random(), random(), random(), 1

        neighbors_colors = {}
        for n in [i for i in range(self.cell_vertices + 2)]:
            neighbors_colors[n] = (random(), random(), random(), 1)

        for cv in self.cells_visual:
            c = cv.cell
            this_distance = distances[c]
            new_col = (this_distance / max_distance if this_distance else 0, 0 if c in longest_path else 1, 1 if type(c) is CellUnder and self.props.cell_thickness >= 0 else 0, 1)
            cv.color_layers[DISTANCE] = new_col

            cv.color_layers[GROUP] = group_colors[c.group]

            cv.color_layers[NEIGHBORS] = neighbors_colors[len(c.links)]

        set_mesh_layers(self.obj_cells, self.cells_visual)
