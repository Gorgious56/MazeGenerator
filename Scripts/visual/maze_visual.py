import bpy
from random import seed, random
from math import pi
from mathutils import Vector
from .. utils . modifier_manager import add_modifier, add_driver_to, WALL_BEVEL_NAME, WALL_WELD_NAME, WALL_SCREW_NAME, WALL_SOLIDIFY_NAME, CELL_SOLIDIFY_NAME, \
    CELL_WELD_NAME, CELL_BEVEL_NAME, CELL_SUBSURF_NAME, CELL_DISPLACE_NAME, CELL_WELD_2_NAME, CELL_CYLINDER_NAME, CELL_WELD_CYLINDER_NAME, \
    CELL_MOEBIUS_NAME, CELL_TORUS_NAME, CELL_WIREFRAME_NAME, CELL_DECIMATE_NAME, CELL_STAIRS_NAME
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
from .. visual . cell_type_manager import POLAR, SQUARE, TRIANGLE, HEXAGON, get_cell_vertices
from .. visual . cell_visual import DISTANCE, GROUP, NEIGHBORS, DISPLACE, STAIRS
from . space_rep_manager import REP_REGULAR, REP_CYLINDER, REP_MEOBIUS, REP_TORUS, REP_BOX, REP_STAIRS


class MazeVisual:
    Instance = None
    Mat_mgr = None

    def __init__(self, scene):
        self.col_objects = None
        self.obj_walls = None
        self.mesh_walls = None
        self.obj_cells = None
        self.mesh_cells = None
        self.obj_cylinder = None
        self.obj_torus = None
        self.grid = None

        self.scene = scene
        self.props = scene.mg_props
        props = self.props

        self.cell_vertices = get_cell_vertices(self.props.cell_type)
        self.cells_vertices = []
        self.cells_visual = []

        self.generate_grid()
        if not algorithm_manager.is_algo_incompatible(props):
            algorithm_manager.work(self.grid, props)
            self.grid.sparse_dead_ends(props.sparse_dead_ends, props.braid_dead_ends, props.seed)
            props.dead_ends = self.grid.braid_dead_ends(props.braid_dead_ends, props.seed)

            self.generate_objects()
            self.build_objects()
            self.generate_modifiers()
            self.generate_drivers()

            self.set_materials()

            self.paint_cells()
            self.update_visibility()

        MazeVisual.Instance = self

    def get_material_manager(self):
        if MazeVisual.Mat_mgr is None:
            MazeVisual.Mat_mgr = MaterialManager(self)
        else:
            MazeVisual.Mat_mgr.update(self)
        return MazeVisual.Mat_mgr

    def update_visibility(self):
        set_hidden = self.props.wall_hide and self.props.cell_inset > 0 or self.props.maze_weave
        self.obj_walls.hide_viewport = bool(set_hidden)
        self.obj_walls.hide_render = bool(set_hidden)

    def generate_grid(self):
        props = self.props

        grid = None
        maze_dimension = int(props.maze_space_dimension)
        if props.cell_type == POLAR:
            grid = GridPolar
        elif props.cell_type == HEXAGON:
            grid = GridHex
        elif props.cell_type == TRIANGLE:
            grid = GridTriangle
        else:
            if props.maze_weave:
                self.grid = GridWeave(
                    rows=props.maze_rows_or_radius,
                    columns=props.maze_columns,
                    levels=1,
                    cell_size=1 - max(0.2, props.cell_inset),
                    use_kruskal=algorithm_manager.is_kruskal_random(props.maze_algorithm),
                    weave=props.maze_weave,
                    space_rep=maze_dimension)
                return
            elif maze_dimension == int(REP_BOX):
                rows = props.maze_rows_or_radius
                cols = props.maze_columns
                self.grid = Grid(
                    rows=3 * rows,
                    columns=2 * cols + 2 * rows,
                    levels=props.maze_levels if maze_dimension == int(REP_REGULAR) else 1,
                    cell_size=1 - props.cell_inset,
                    space_rep=maze_dimension,
                    mask=[
                        (0, 0, rows - 1, rows - 1),
                        (rows + cols, 0, 2 * rows + 2 * cols - 1, rows - 1),
                        (0, 2 * rows, rows - 1, 3 * rows - 1),
                        (rows + cols, 2 * rows, 2 * rows + 2 * cols - 1, 3 * rows - 1)])
                return
            else:
                grid = Grid
        self.grid = grid(
            rows=props.maze_rows_or_radius,
            columns=props.maze_columns,
            levels=props.maze_levels if maze_dimension == int(REP_REGULAR) else 1,
            cell_size=1 - props.cell_inset,
            space_rep=maze_dimension)

    def generate_objects(self):
        scene = self.scene
        # Get or add the Wall mesh.
        try:
            self.mesh_wall = bpy.data.meshes['MG_Wall Mesh']
            self.mesh_wall.clear_geometry()
        except KeyError:
            self.mesh_wall = bpy.data.meshes.new("MG_Wall Mesh")

        # Get or add the Wall object and link it to the wall mesh.
        try:
            self.obj_walls = scene.objects['MG_Walls']
        except KeyError:
            self.obj_walls = bpy.data.objects.new('MG_Walls', self.mesh_wall)
            scene.collection.objects.link(self.obj_walls)

        # Get or add the Cells mesh.
        try:
            self.mesh_cells = bpy.data.meshes['MG_Cells Mesh']
            self.mesh_cells.clear_geometry()
        except KeyError:
            self.mesh_cells = bpy.data.meshes.new("MG_Cells Mesh")

        # Get or add the Wall object and link it to the wall mesh.
        try:
            self.obj_cells = scene.objects['MG_Cells']
        except KeyError:
            self.obj_cells = bpy.data.objects.new('MG_Cells', self.mesh_cells)
            scene.collection.objects.link(self.obj_cells)

        # Get or add the cylinder curver object.
        try:
            self.obj_cylinder = scene.objects['MG_Curver_Cyl']
        except KeyError:
            bpy.ops.curve.primitive_bezier_circle_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), rotation=(pi / 2, 0, 0))
            self.obj_cylinder = bpy.context.active_object
            self.obj_cylinder.name = 'MG_Curver_Cyl'
        self.obj_cylinder.hide_viewport = True
        self.obj_cylinder.hide_render = True

        try:
            self.obj_torus = scene.objects['MG_Curver_Tor']
        except KeyError:
            bpy.ops.curve.primitive_bezier_circle_add(enter_editmode=False, align='WORLD', location=(0, 0, 0))
            self.obj_torus = bpy.context.active_object
            self.obj_torus.name = 'MG_Curver_Tor'
        self.obj_torus.hide_viewport = True
        self.obj_torus.hide_render = True

        # Put everything in a master collection.
        try:
            self.col_objects = bpy.data.collections['MG_Collection']
        except KeyError:
            self.col_objects = bpy.data.collections.new(name='MG_Collection')
        try:
            bpy.context.scene.collection.children.link(self.col_objects)
        except RuntimeError:
            pass

        for obj in (self.obj_cells, self.obj_cylinder, self.obj_walls, self.obj_torus):
            for col in obj.users_collection:
                col.objects.unlink(obj)  # Unlink it from master collection.
            self.col_objects.objects.link(obj)  # Link it with MG collection.

    def generate_modifiers(self):
        props = self.props
        ow = props.auto_overwrite or CELL_STAIRS_NAME not in self.obj_walls.modifiers

        add_modifier(self.obj_walls, 'DISPLACE', CELL_STAIRS_NAME, properties={'show_expanded': False, 'direction': 'Z', 'vertex_group': STAIRS, 'mid_level': 0}, overwrite_props=ow)
        add_modifier(self.obj_walls, 'WELD', WALL_WELD_NAME, properties={'show_expanded': False}, overwrite_props=ow)
        add_modifier(self.obj_walls, 'SCREW', WALL_SCREW_NAME, properties={'show_expanded': False, 'angle': 0, 'steps': 1, 'render_steps': 1, 'screw_offset': props.wall_height}, overwrite_props=ow)
        add_modifier(self.obj_walls, 'SOLIDIFY', WALL_SOLIDIFY_NAME, properties={'show_expanded': False, 'solidify_mode': 'NON_MANIFOLD', 'thickness': props.wall_width, 'offset': 0}, overwrite_props=ow)
        add_modifier(self.obj_walls, 'BEVEL', WALL_BEVEL_NAME, properties={'show_expanded': False, 'segments': 4, 'limit_method': 'ANGLE', 'use_clamp_overlap': False}, overwrite_props=ow)
        add_modifier(self.obj_walls, 'DISPLACE', CELL_DISPLACE_NAME, properties={'show_expanded': False, 'direction': 'Z', 'mid_level': 0.5}, overwrite_props=ow)
        add_modifier(self.obj_walls, 'SIMPLE_DEFORM', CELL_MOEBIUS_NAME, properties={'show_expanded': False, 'angle': 2 * pi + (1 / 16 if props.cell_type == TRIANGLE else 0)}, overwrite_props=ow)
        add_modifier(self.obj_walls, 'CURVE', CELL_CYLINDER_NAME, properties={'show_expanded': False, 'object': self.obj_cylinder}, overwrite_props=ow)
        add_modifier(self.obj_walls, 'CURVE', CELL_TORUS_NAME, properties={'show_expanded': False, 'object': self.obj_torus, 'deform_axis': 'POS_Y'}, overwrite_props=ow)
        add_modifier(self.obj_walls, 'WELD', CELL_WELD_CYLINDER_NAME, properties={'show_expanded': False, 'merge_threshold': 0.1}, overwrite_props=ow)
        
        add_modifier(self.obj_cells, 'DISPLACE', CELL_STAIRS_NAME, properties={'show_expanded': False, 'direction': 'Z', 'vertex_group': STAIRS, 'mid_level': 0}, overwrite_props=ow)
        add_modifier(self.obj_cells, 'WELD', CELL_WELD_NAME, properties={'show_expanded': False, 'vertex_group': DISPLACE, 'invert_vertex_group': True, 'merge_threshold': 0.04}, overwrite_props=ow)
        add_modifier(self.obj_cells, 'WELD', CELL_WELD_2_NAME, properties={'show_expanded': False, 'vertex_group': DISPLACE, 'invert_vertex_group': False}, overwrite_props=ow)
        add_modifier(self.obj_cells, 'SOLIDIFY', CELL_SOLIDIFY_NAME, properties={'show_expanded': False, 'use_even_offset': True, 'vertex_group': DISPLACE, 'invert_vertex_group': True}, overwrite_props=ow)

        add_modifier(self.obj_cells, 'DISPLACE', CELL_DISPLACE_NAME, properties={'show_expanded': False, 'direction': 'Z', 'vertex_group': DISPLACE, 'mid_level': 0}, overwrite_props=ow)
        add_modifier(self.obj_cells, 'SIMPLE_DEFORM', CELL_MOEBIUS_NAME, properties={'show_expanded': False, 'angle': 2 * pi + (1 / 18 if props.cell_type == TRIANGLE else 0)}, overwrite_props=ow)
        add_modifier(self.obj_cells, 'CURVE', CELL_CYLINDER_NAME, properties={'show_expanded': False, 'object': self.obj_cylinder}, overwrite_props=ow)
        add_modifier(self.obj_cells, 'CURVE', CELL_TORUS_NAME, properties={'show_expanded': False, 'object': self.obj_torus, 'deform_axis': 'POS_Y'}, overwrite_props=ow)
        add_modifier(self.obj_cells, 'WELD', CELL_WELD_CYLINDER_NAME, properties={'show_expanded': False, 'merge_threshold': 0.05}, overwrite_props=ow)
        add_modifier(self.obj_cells, 'DECIMATE', CELL_DECIMATE_NAME, properties={'show_expanded': False}, overwrite_props=ow)
        add_modifier(self.obj_cells, 'SUBSURF', CELL_SUBSURF_NAME, properties={'show_expanded': False}, overwrite_props=ow)
        add_modifier(self.obj_cells, 'BEVEL', CELL_BEVEL_NAME, properties={'show_expanded': False, 'segments': 2, 'limit_method': 'ANGLE', 'material': 1, 'profile': 1, 'angle_limit': 0.75, 'use_clamp_overlap': False}, overwrite_props=ow)
        add_modifier(self.obj_cells, 'WIREFRAME', CELL_WIREFRAME_NAME, properties={'show_expanded': False, 'use_replace': False, 'material_offset': 1}, overwrite_props=ow)

        self.generate_drivers(ow)

    def generate_drivers(self, force=False):
        if self.props.auto_overwrite or force:
            drivers_dic = \
                {
                    self.obj_walls: {
                        CELL_STAIRS_NAME: (
                            ('strength', 'maze_stairs_scale', 'var'),
                            ('show_viewport', 'maze_space_dimension', 'int(var) == ' + REP_STAIRS),
                            ('show_render', 'maze_space_dimension', 'int(var) == ' + REP_STAIRS),
                        ),
                        WALL_WELD_NAME: (
                            ('merge_threshold', 'maze_stairs_weld', None),
                        ),
                        WALL_SCREW_NAME: (
                            ('screw_offset', 'wall_height', None),
                            ('use_smooth_shade', 'wall_bevel', 'var > 0.005'),
                        ),
                        WALL_SOLIDIFY_NAME: (
                            ('thickness', 'wall_width', None),
                            ('show_viewport', 'wall_width', 'var != 0'),
                            ('show_render', 'wall_width', 'var != 0')
                        ),
                        WALL_BEVEL_NAME: (
                            ('width', 'wall_bevel', None),
                            ('show_viewport', 'wall_bevel', 'var != 0'),
                            ('show_render', 'wall_bevel', 'var != 0')
                        ),
                        CELL_CYLINDER_NAME: (
                            ('show_viewport', 'maze_space_dimension', REP_BOX + ' > int(var) > ' + REP_STAIRS),
                            ('show_render', 'maze_space_dimension', REP_BOX + ' > int(var) > ' + REP_STAIRS)
                        ),
                        CELL_DISPLACE_NAME: (
                            ('strength', 'wall_height', '-var'),
                            ('show_viewport', 'maze_space_dimension', 'int(var) == ' + REP_CYLINDER + ' or int(var) == ' + REP_MEOBIUS),
                            ('show_render', 'maze_space_dimension', 'int(var) == ' + REP_CYLINDER + ' or int(var) == ' + REP_MEOBIUS)
                        ),
                        CELL_MOEBIUS_NAME: (
                            ('show_viewport', 'maze_space_dimension', 'int(var) == ' + REP_MEOBIUS),
                            ('show_render', 'maze_space_dimension', 'int(var) == ' + REP_MEOBIUS)
                        ),
                        CELL_TORUS_NAME: (
                            ('show_viewport', 'maze_space_dimension', 'int(var) == ' + REP_TORUS),
                            ('show_render', 'maze_space_dimension', 'int(var) == ' + REP_TORUS)
                        ),
                        CELL_WELD_CYLINDER_NAME: (
                            ('show_viewport', 'maze_space_dimension', REP_BOX + " > int(var) > " + REP_STAIRS),
                            ('show_render', 'maze_space_dimension', REP_BOX + " > int(var) > " + REP_STAIRS)
                        )
                    },
                    self.obj_cells: {
                        CELL_STAIRS_NAME: (
                            ('strength', 'maze_stairs_scale', 'var'),
                            ('show_viewport', 'maze_space_dimension', 'int(var) ==' + REP_STAIRS),
                            ('show_render', 'maze_space_dimension', 'int(var) ==' + REP_STAIRS),
                        ),
                        CELL_WELD_NAME: (
                            ('merge_threshold', 'maze_stairs_weld', None),
                        ),
                        CELL_WELD_2_NAME: (
                            ('show_viewport', 'maze_weave', 'var != 0'),
                            ('show_render', 'maze_weave', 'var != 0')
                        ),
                        CELL_SOLIDIFY_NAME: (
                            ('offset', 'maze_space_dimension', '-1 if int(var) == ' + REP_REGULAR + ' or int(var) == ' + REP_STAIRS + ' else 0'),
                            ('thickness', 'cell_thickness', None),
                            ('thickness_vertex_group', 'cell_thickness', 'max(0, 1 - abs(var / 2))'),
                            ('show_viewport', 'cell_thickness', 'var != 0'),
                            ('show_render', 'cell_thickness', 'var != 0')
                        ),
                        CELL_DECIMATE_NAME: (
                            ('ratio', 'cell_decimate', '1 - var / 100'),
                            ('show_viewport', 'cell_decimate', 'var > 0'),
                            ('show_render', 'cell_decimate', 'var > 0')
                        ),
                        CELL_SUBSURF_NAME: (
                            ('levels', 'cell_subdiv', None),
                            ('render_levels', 'cell_subdiv', None),
                            ('show_viewport', 'cell_subdiv', 'var > 0'),
                            ('show_render', 'cell_subdiv', 'var > 0')
                        ),
                        CELL_DISPLACE_NAME: (
                            ('strength', 'cell_thickness', '- (var + (abs(var) / var * 0.1)) if var != 0 else 0'),
                            ('show_viewport', 'cell_thickness', 'var != 0'),
                            ('show_render', 'cell_thickness', 'var != 0')
                        ),
                        CELL_MOEBIUS_NAME: (
                            ('show_viewport', 'maze_space_dimension', "int(var) == " + REP_MEOBIUS),
                            ('show_render', 'maze_space_dimension', "int(var) == " + REP_MEOBIUS)
                        ),
                        CELL_TORUS_NAME: (
                            ('show_viewport', 'maze_space_dimension', "int(var) == " + REP_TORUS),
                            ('show_render', 'maze_space_dimension', "int(var) == " + REP_TORUS)
                        ),
                        CELL_CYLINDER_NAME: (
                            ('show_viewport', 'maze_space_dimension', REP_BOX + " > int(var) > " + REP_STAIRS),
                            ('show_render', 'maze_space_dimension', REP_BOX + " > int(var) > " + REP_STAIRS)
                        ),
                        CELL_WELD_CYLINDER_NAME: (
                            ('show_viewport', 'maze_space_dimension', REP_BOX + " > int(var) > " + REP_STAIRS),
                            ('show_render', 'maze_space_dimension', REP_BOX + " > int(var) > " + REP_STAIRS)
                        ),
                        CELL_WIREFRAME_NAME: (
                            ('show_viewport', 'cell_wireframe', 'var != 0'),
                            ('show_render', 'cell_wireframe', 'var != 0'),
                            ('thickness', 'cell_wireframe', None)),
                        CELL_BEVEL_NAME: (
                            ('show_render', 'cell_contour', 'var != 0'),
                            ('show_viewport', 'cell_contour', 'var != 0'),
                            ('width', 'cell_contour', None),
                            ('segments', 'cell_contour_black', '2 if var else 4'),
                            ('profile', 'cell_contour_black', '1 if var else 0.5'),
                            ('material', 'cell_contour_black', '1 if var else 0'),
                        )
                    }
                }

            for obj, dic in drivers_dic.items():
                for mod_name, drivers in dic.items():
                    for driver in drivers:
                        add_driver_to(obj.modifiers[mod_name], driver[0], 'var', 'SCENE', self.scene, 'mg_props.' + driver[1], expression=driver[2])

            # Scale the cylinder object when scaling the size of the maze
            for i, obj in enumerate((self.obj_cylinder, self.obj_torus)):
                drvList = obj.driver_add('scale')
                for fc in drvList:
                    drv = fc.driver
                    try:
                        var = drv.variables[0]
                    except IndexError:
                        var = drv.variables.new()

                    var.name = 'var'
                    var.type = 'SINGLE_PROP'

                    target = var.targets[0]
                    target.id_type = 'SCENE'
                    target.id = self.scene
                    target.data_path = 'mg_props.maze_columns' if i == 0 else 'mg_props.maze_rows_or_radius'

                    exp = 'var * 0.314'
                    if self.props.cell_type == SQUARE:
                        exp = 'var * 0.15915'
                    elif self.props.cell_type == TRIANGLE:
                        if i == 0:
                            exp = 'var * 0.07963'
                        else:
                            exp = 'var * 0.13791'
                    elif self.props.cell_type == HEXAGON:
                        if i == 0:
                            exp = 'var * 0.2388'
                        else:
                            exp = 'var * 0.2758'

                    drv.expression = exp

    def build_objects(self):
        self.cells_visual = self.grid.get_blueprint()

        walls_corners = []
        walls_edges = []
        vertices = 0
        for cv in self.cells_visual:
            for f in cv.faces:
                wall_corners = f.wall_corners()
                if wall_corners:
                    walls_corners.extend(wall_corners)
                    for i in range(len(wall_corners) // 2):
                        walls_edges.append((vertices, vertices + 1))
                        vertices += 2
                    f.translate_walls_indices(vertices - len(wall_corners))

        self.mesh_wall.from_pydata(
            walls_corners,
            walls_edges,
            [])

        cells_corners = []
        cells_edges = []
        cells_faces = []
        vertices = 0
        for cv in self.cells_visual:
            for f in cv.faces:
                f.translate_indices(vertices)
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
        for mesh in (self.mesh_cells, self.mesh_wall):
            mesh.use_auto_smooth = True
            mesh.auto_smooth_angle = 0.5

    def update_cell_smooth(self):
        smooth = self.props.cell_use_smooth
        for p in self.mesh_cells.polygons:
            p.use_smooth = smooth

    def set_materials(self):
        self.get_material_manager().set_materials()

    def paint_cells(self):
        linked_cells = self.grid.get_linked_cells()

        distances = Distances(self.grid.get_random_linked_cell(_seed=self.props.seed))
        distances.get_distances()
        new_start, distance = distances.max()
        distances = Distances(new_start)
        distances.get_distances()
        goal, max_distance = distances.max()

        longest_path = distances.path_to(goal).path

        # Avoid flickering when the algorithm randomly chooses start and end cells.
        start = longest_path[0]
        start = (start.row, start.column, start.level)
        last_start = self.props.maze_last_start_cell
        last_start = (last_start[0], last_start[1], last_start[2])
        if start != last_start:
            goal = longest_path[-1]
            goal = (goal.row, goal.column, goal.level)
            if goal == last_start:
                distances.reverse()
            else:
                self.props.maze_last_start_cell = start
        # End.

        seed(self.props.seed_color)

        groups = set()
        group_colors = {}
        for c in linked_cells:
            groups.add(c.group)
        for g in groups:
            group_colors[g] = random(), random(), random(), 1

        neighbors_colors = {}
        for n in [i for i in range(self.cell_vertices + 5)]:
            neighbors_colors[n] = (random(), random(), random(), 1)

        for cv in self.cells_visual:
            c = cv.cell
            this_distance = distances[c]
            relative_distance = 0 if this_distance is None else this_distance / max_distance
            new_col = (relative_distance, 0 if c in longest_path else 1, 1 if type(c) is CellUnder and self.props.cell_thickness >= 0 else 0, 0 if this_distance is not None else 1)
            cv.color_layers[DISTANCE] = new_col

            cv.color_layers[GROUP] = group_colors[c.group]

            cv.color_layers[NEIGHBORS] = neighbors_colors[len(c.links)]

            for f in cv.faces:
                f.set_vertex_group(STAIRS, [relative_distance] * f.corners())
                f.set_wall_vertex_groups(STAIRS, [relative_distance] * f.wall_vertices())

        set_mesh_layers(self.obj_cells, self.obj_walls, self.cells_visual)
