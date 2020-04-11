import bpy
from Scripts.utils.mesh_manager import MeshManager


class MazeVisual:
    Instance = None
    Mat_mgr = None
    col_objects = None
    obj_walls = None
    mesh_walls = None
    obj_cells = None
    mesh_cells = None
    obj_cylinder = None
    obj_torus = None
    tex_disp = None
    grid = None
    scene = None
    props = None

        MeshManager.create_vertex_groups(MazeVisual.obj_cells, MazeVisual.obj_walls)

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
            MeshManager.create_vertex_groups(MazeVisual.obj_cells, MazeVisual.obj_walls)
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
        set_hidden = (self.props.wall_hide and self.props.cell_inset > 0) or (self.props.maze_weave and algorithm_manager.is_algo_weaved(self.props))
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

    def generate_objects():
        self = MazeVisual
        scene = self.scene
        self.col_objects = bpy.data.collections.get('MG_Collection', bpy.data.collections.new(name='MG_Collection'))
        if self.col_objects not in bpy.context.scene.collection.children[:]:
            bpy.context.scene.collection.children.link(self.col_objects)

        self.mesh_wall = bpy.data.meshes.get('MG_Wall Mesh', bpy.data.meshes.new("MG_Wall Mesh"))
        self.obj_walls = scene.objects.get('MG_Walls', bpy.data.objects.new('MG_Walls', self.mesh_wall))

        self.mesh_cells = bpy.data.meshes.get('MG_Cells Mesh', bpy.data.meshes.new("MG_Cells Mesh"))
        self.obj_cells = scene.objects.get('MG_Cells', bpy.data.objects.new('MG_Cells', self.mesh_cells))

        self.obj_cylinder = scene.objects.get('MG_Curver_Cyl')
        if not self.obj_cylinder:
            bpy.ops.curve.primitive_bezier_circle_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), rotation=(math.pi / 2, 0, 0))            
            self.obj_cylinder = bpy.context.active_object
            self.obj_cylinder.name = 'MG_Curver_Cyl'
        self.obj_cylinder.hide_viewport = self.obj_cylinder.hide_render = True

        self.obj_torus = scene.objects.get('MG_Curver_Tor')
        if not self.obj_torus:
            bpy.ops.curve.primitive_bezier_circle_add(enter_editmode=False, align='WORLD', location=(0, 0, 0))
            self.obj_torus = bpy.context.active_object
            self.obj_torus.name = 'MG_Curver_Tor'
        self.obj_torus.hide_viewport = self.obj_torus.hide_render = True

        for obj in (self.obj_cells, self.obj_cylinder, self.obj_walls, self.obj_torus):
            for col in obj.users_collection:
                col.objects.unlink(obj)
            self.col_objects.objects.link(obj)

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

        MeshManager.set_mesh_layers(self.obj_cells, self.obj_walls, cells_visual)


class MaterialManager:
    cell_rgb_node = None
    cell_vertex_colors_node = None
    cell_sep_rgb_node = None
    cell_value_node = None
    cell_math_node = None
    cell_math_alpha_node = None
    cell_cr_distance_node = None
    cell_mix_longest_distance_node = None
    cell_mix_under_node = None
    cell_hsv_node = None
    cell_bsdf_node = None
    cell_output_node = None

    def init_cell_rgb_node(self, nodes, props):
        try:
            self.cell_rgb_node = nodes['cell_rgb_node']
        except KeyError:
            self.cell_rgb_node = nodes.new(type='ShaderNodeRGB')
            self.cell_rgb_node.name = 'cell_rgb_node'
        finally:
            random.seed(props.seed_color)
            self.cell_rgb_node.outputs['Color'].default_value = (random.random(), random.random(), random.random(), 1)
            self.cell_rgb_node.location = -400, -300

    def init_cell_vertex_colors_node(self, nodes, props):
        try:
            self.cell_vertex_colors_node = nodes['cell_vertex_colors_node']
        except KeyError:
            self.cell_vertex_colors_node = nodes.new(type='ShaderNodeVertexColor')
            self.cell_vertex_colors_node.name = 'cell_vertex_colors_node'
        finally:
            self.cell_vertex_colors_node.layer_name = props.paint_style
            self.cell_vertex_colors_node.location = -1200, 0

    def init_cell_hsv_node(self, nodes, scene):
        try:
            self.cell_hsv_node = nodes['cell_hsv_node']
        except KeyError:
            self.cell_hsv_node = nodes.new(type='ShaderNodeHueSaturation')
            self.cell_hsv_node.name = 'cell_hsv_node'
        finally:
            self.cell_hsv_node.location = -200, 0
            if scene:
                mod_mgr.add_driver_to(self.cell_hsv_node.inputs['Hue'], 'default_value', 'hue_shift', 'SCENE', scene, 'mg_props.hue_shift', '0.5 + hue_shift')
                mod_mgr.add_driver_to(self.cell_hsv_node.inputs['Saturation'], 'default_value', 'sat_shift', 'SCENE', scene, 'mg_props.saturation_shift', '1 + sat_shift')
                mod_mgr.add_driver_to(self.cell_hsv_node.inputs['Value'], 'default_value', 'val_shift', 'SCENE', scene, 'mg_props.value_shift', '1 + val_shift')

    def init_cell_bsdf_node(self, nodes):
        try:
            self.cell_bsdf_node = nodes['cell_bsdf_node']
        except KeyError:
            self.cell_bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
            self.cell_bsdf_node.name = 'cell_bsdf_node'

    def init_cell_sep_rgb_node(self, nodes):
        try:
            self.cell_sep_rgb_node = nodes['cell_sep_rgb_node']
        except KeyError:
            self.cell_sep_rgb_node = nodes.new(type='ShaderNodeSeparateRGB')
            self.cell_sep_rgb_node.name = 'cell_sep_rgb_node'
        finally:
            self.cell_sep_rgb_node.location = -1000, 0

    def init_cell_mix_distance_node(self, nodes, props):
        try:
            self.cell_cr_distance_node = nodes['cell_cr_distance_node']
        except KeyError:
            self.cell_cr_distance_node = nodes.new(type='ShaderNodeValToRGB')
            self.cell_cr_distance_node.name = 'cell_cr_distance_node'
            self.cell_cr_distance_node.color_ramp.elements[0].color = (0, 1, 0, 1)
            self.cell_cr_distance_node.color_ramp.elements[1].color = [1, 0, 0, 1]
        finally:
            self.cell_cr_distance_node.location = -800, -100

    def init_cell_math_node(self, nodes, props):
        try:
            self.cell_math_node = nodes['cell_math_node']
        except KeyError:
            self.cell_math_node = nodes.new(type='ShaderNodeMath')
            self.cell_math_node.name = 'cell_math_node'
        finally:
            self.cell_math_node.operation = 'MULTIPLY'
            self.cell_math_node.inputs[1].default_value = props.show_only_longest_path
            self.cell_math_node.location = -800, 100

    def init_cell_math_alpha_node(self, nodes):
        try:
            self.cell_math_alpha_node = nodes['cell_math_alpha_node']
        except KeyError:
            self.cell_math_alpha_node = nodes.new(type='ShaderNodeMath')
            self.cell_math_alpha_node.name = 'cell_math_alpha_node'
        finally:
            self.cell_math_alpha_node.operation = 'ADD'
            self.cell_math_alpha_node.location = -800, 300

    def init_cell_value_node(self, nodes):
        try:
            self.cell_value_node = nodes['cell_value_node']
        except KeyError:
            self.cell_value_node = nodes.new(type='ShaderNodeValue')
            self.cell_value_node.name = 'cell_value_node'
        finally:
            self.cell_value_node.location = -1000, -400

    def init_cell_mix_under_node(self, nodes):
        try:
            self.cell_mix_under_node = nodes['cell_mix_under_node']
        except KeyError:
            self.cell_mix_under_node = nodes.new(type='ShaderNodeMixRGB')
            self.cell_mix_under_node.name = 'cell_mix_under_node'
        finally:
            self.cell_mix_under_node.blend_type = 'SUBTRACT'
            self.cell_mix_under_node.inputs[0].default_value = 0.5
            self.cell_mix_under_node.location = -800, -400

    def init_cell_mix_longest_distance_node(self, nodes):
        try:
            self.cell_mix_longest_distance_node = nodes['cell_mix_longest_distance_node']
        except KeyError:
            self.cell_mix_longest_distance_node = nodes.new(type='ShaderNodeMixRGB')
            self.cell_mix_longest_distance_node.name = 'cell_mix_longest_distance_node'
        finally:
            self.cell_mix_longest_distance_node.inputs[2].default_value = [0.5, 0.5, 0.5, 1]
            self.cell_mix_longest_distance_node.location = -400, 0

    def init_cell_output_node(self, nodes):
        try:
            self.cell_output_node = nodes['cell_output_node']
        except KeyError:
            self.cell_output_node = nodes.new(type='ShaderNodeOutputMaterial')
            self.cell_output_node.name = 'cell_output_node'
        finally:
            self.cell_output_node.location = 300, 0

    def set_materials():
        MaterialManager.set_cell_material()
        MaterialManager.set_cell_contour_material()
        MaterialManager.set_wall_material()

    def set_cell_material():
        self = MaterialManager
        already_created = False
        obj_cells = MazeVisual.obj_cells
        props = MazeVisual.props
        scene = MazeVisual.scene

        try:
            mat = obj_cells.material_slots[0].material
            already_created = True
        except IndexError:
            mat = bpy.data.materials.new("mat_cells")
            obj_cells.data.materials.append(mat)
        mat.use_nodes = True

        nodes = mat.node_tree.nodes
        if not already_created or props.auto_overwrite:
            nodes.clear()

        self.init_cell_rgb_node(MaterialManager, nodes, props)
        self.init_cell_vertex_colors_node(MaterialManager, nodes, props)
        self.init_cell_hsv_node(MaterialManager, nodes, scene)
        self.init_cell_sep_rgb_node(MaterialManager, nodes)
        self.init_cell_mix_distance_node(MaterialManager, nodes, props)
        self.init_cell_math_node(MaterialManager, nodes, props)
        self.init_cell_math_alpha_node(MaterialManager, nodes)
        self.init_cell_value_node(MaterialManager, nodes)
        self.init_cell_mix_under_node(MaterialManager, nodes)
        self.init_cell_mix_longest_distance_node(MaterialManager, nodes)
        self.init_cell_bsdf_node(MaterialManager, nodes)
        self.init_cell_output_node(MaterialManager, nodes)

        try:
            self.cell_vertex_colors_node.layer_name = props.paint_style
            links = mat.node_tree.links
            if props.paint_style == DISTANCE:
                links.new(self.cell_vertex_colors_node.outputs[0], self.cell_sep_rgb_node.inputs[0])
                links.new(self.cell_sep_rgb_node.outputs[0], self.cell_cr_distance_node.inputs[0])
                links.new(self.cell_sep_rgb_node.outputs[1], self.cell_math_node.inputs[0])
                links.new(self.cell_value_node.outputs[0], self.cell_mix_under_node.inputs[1])
                links.new(self.cell_sep_rgb_node.outputs[2], self.cell_mix_under_node.inputs[2])
                links.new(self.cell_mix_under_node.outputs[0], self.cell_hsv_node.inputs[2])

                links.new(self.cell_math_node.outputs[0], self.cell_math_alpha_node.inputs[0])
                links.new(self.cell_vertex_colors_node.outputs[1], self.cell_math_alpha_node.inputs[1])
                links.new(self.cell_math_alpha_node.outputs[0], self.cell_mix_longest_distance_node.inputs[0])

                links.new(self.cell_cr_distance_node.outputs[0], self.cell_mix_longest_distance_node.inputs[1])
                links.new(self.cell_mix_longest_distance_node.outputs[0], self.cell_hsv_node.inputs[4])

                mod_mgr.add_driver_to(self.cell_value_node.outputs[0], 'default_value', 'val_shift', 'SCENE', scene, 'mg_props.value_shift', '1 + val_shift')
                mod_mgr.add_driver_to(self.cell_mix_under_node.inputs[0], 'default_value', 'val_shift', 'SCENE', scene, 'mg_props.value_shift', '(val_shift + 1)/2')
            elif props.paint_style == UNIFORM:
                links.new(self.cell_rgb_node.outputs[0], self.cell_hsv_node.inputs[4])
            else:
                links.new(self.cell_vertex_colors_node.outputs[0], self.cell_hsv_node.inputs[4])

            links.new(self.cell_hsv_node.outputs[0], self.cell_bsdf_node.inputs[0])
            links.new(self.cell_bsdf_node.outputs[0], self.cell_output_node.inputs[0])

        except IndexError:
            pass
        except AttributeError:
            pass

    def set_cell_contour_material():
        props = MazeVisual.props
        obj_cells = MazeVisual.obj_cells
        try:
            mat = obj_cells.material_slots[1].material
            if not props.auto_overwrite:
                return
        except IndexError:
            mat = bpy.data.materials.new("mat_cells_contour")
            obj_cells.data.materials.append(mat)
        mat.use_nodes = True

        mat.node_tree.nodes['Principled BSDF'].inputs[0].default_value = (0, 0, 0, 1)
        mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 1

    def set_wall_material():
        props = MazeVisual.props
        obj_walls = MazeVisual.obj_walls
        try:
            mat = obj_walls.material_slots[0].material
            if not props.auto_overwrite:
                return
        except IndexError:
            mat = bpy.data.materials.new("mat_walls")
            obj_walls.data.materials.append(mat)
        mat.use_nodes = True

        nodes = mat.node_tree.nodes
        nodes.clear()

        vertex_colors = nodes.new(type='ShaderNodeRGB')
        vertex_colors.location = -400, 0
        color = props.wall_color
        vertex_colors.outputs['Color'].default_value = [color[0], color[1], color[2], 1]

        principled = nodes.new(type='ShaderNodeBsdfPrincipled')

        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = 300, 0

        links = mat.node_tree.links
        links.new(vertex_colors.outputs[0], principled.inputs[0])
        links.new(principled.outputs[0], output.inputs[0])
