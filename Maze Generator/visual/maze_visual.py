import bpy
import random
import math
from ..utils import modifier_manager as mod_mgr
from ..utils.distance_manager import Distances
from ..utils.mesh_manager import MeshManager
from ..maze_logic.data_structure import grids
from ..maze_logic import algorithm_manager
from ..visual.cell_type_manager import POLAR, SQUARE, TRIANGLE, HEXAGON
from ..visual import space_rep_manager as sp_rep
from ..visual.cell_visual import DISTANCE, GROUP, NEIGHBORS, VG_DISPLACE, VG_STAIRS, UNIFORM


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

    def refresh_maze(scene):
        MazeVisual.scene = scene
        MazeVisual.props = scene.mg_props
        MazeVisual.generate_objects()
        MazeVisual.generate_textures()
        MaterialManager.set_materials()
        MeshManager.create_vertex_groups(MazeVisual.obj_cells, MazeVisual.obj_walls)
        mod_mgr.setup_modifiers_and_drivers(MazeVisual)

    def generate_maze(scene):
        self = MazeVisual
        self.scene = scene
        self.props = scene.mg_props
        props = self.props

        self.generate_grid()
        if not algorithm_manager.is_algo_incompatible(props):
            algorithm_manager.work(self.grid, props)
            self.grid.sparse_dead_ends(props.sparse_dead_ends, props.braid_dead_ends, props.seed)
            props.dead_ends = self.grid.braid_dead_ends(props.braid_dead_ends, props.seed)

            self.generate_objects()
            self.generate_textures()
            self.build_objects()
            MeshManager.create_vertex_groups(MazeVisual.obj_cells, MazeVisual.obj_walls)
            mod_mgr.setup_modifiers_and_drivers(MazeVisual)

            MaterialManager.set_materials()

            self.update_wall_visibility()

    def update_wall_visibility():
        MazeVisual.obj_walls.hide_viewport = MazeVisual.obj_walls.hide_render = \
            (MazeVisual.props.wall_hide and MazeVisual.props.cell_inset > 0) \
            or (MazeVisual.props.maze_weave and algorithm_manager.is_algo_weaved(MazeVisual.props))

    def generate_grid():
        self = MazeVisual
        props = self.props

        grid = None
        maze_dimension = int(props.maze_space_dimension)
        if props.cell_type == POLAR:
            grid = grids.GridPolar
        elif props.cell_type == HEXAGON:
            grid = grids.GridHex
        elif props.cell_type == TRIANGLE:
            grid = grids.GridTriangle
        else:
            if props.maze_weave:
                self.grid = grids.GridWeave(
                    rows=props.maze_rows_or_radius,
                    columns=props.maze_columns,
                    levels=1,
                    cell_size=1 - max(0.2, props.cell_inset),
                    use_kruskal=algorithm_manager.is_kruskal_random(props.maze_algorithm),
                    weave=props.maze_weave,
                    space_rep=maze_dimension)
                return
            elif maze_dimension == int(sp_rep.REP_BOX):
                rows = props.maze_rows_or_radius
                cols = props.maze_columns
                self.grid = grids.Grid(
                    rows=3 * rows,
                    columns=2 * cols + 2 * rows,
                    levels=props.maze_levels if maze_dimension == int(sp_rep.REP_REGULAR) else 1,
                    cell_size=1 - props.cell_inset,
                    space_rep=maze_dimension,
                    mask=[
                        (0, 0, rows - 1, rows - 1),
                        (rows + cols, 0, 2 * rows + 2 * cols - 1, rows - 1),
                        (0, 2 * rows, rows - 1, 3 * rows - 1),
                        (rows + cols, 2 * rows, 2 * rows + 2 * cols - 1, 3 * rows - 1)])
                return
            else:
                grid = grids.Grid
        self.grid = grid(
            rows=props.maze_rows_or_radius,
            columns=props.maze_columns,
            levels=props.maze_levels if maze_dimension == int(sp_rep.REP_REGULAR) else 1,
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

    def generate_textures():
        self = MazeVisual
        tex_disp_name = 'MG_Tex_Disp'

        try:
            self.tex_disp = bpy.data.textures[tex_disp_name]
        except KeyError:
            self.tex_disp = bpy.data.textures.new(name=tex_disp_name, type='CLOUDS')
            self.tex_disp.noise_scale = 50
        self.tex_disp.cloud_type = 'COLOR'

    def build_objects():
        self = MazeVisual
        cells_visual = self.grid.get_blueprint()

        walls_corners = []
        walls_edges = []
        vertices = 0
        for cv in cells_visual:
            for f in cv.faces:
                wall_corners = f.wall_corners()
                if wall_corners:
                    walls_corners.extend(wall_corners)
                    for i in range(len(wall_corners) // 2):
                        walls_edges.append((vertices, vertices + 1))
                        vertices += 2
                    f.translate_walls_indices(vertices - len(wall_corners))

        self.mesh_wall.clear_geometry()
        self.mesh_wall.from_pydata(
            walls_corners,
            walls_edges,
            [])

        cells_corners = []
        cells_faces = []
        vertices = 0
        for cv in cells_visual:
            for f in cv.faces:
                f.translate_indices(vertices)
                cells_corners.extend(f.vertices)
                cells_faces.append(f.face)
                vertices += f.corners()

        self.mesh_cells.clear_geometry()
        self.mesh_cells.from_pydata(
            cells_corners,
            [],
            cells_faces
        )

        if self.props.cell_use_smooth:  # Update only when the mesh is supposed to be smoothed, because the default will be unsmoothed
            self.update_cell_smooth()
        for mesh in (self.mesh_cells, self.mesh_wall):
            mesh.use_auto_smooth = True
            mesh.auto_smooth_angle = 0.5

        MazeVisual.paint_cells(cells_visual)

    @staticmethod
    def update_cell_smooth():
        smooth = MazeVisual.props.cell_use_smooth
        for p in MazeVisual.mesh_cells.polygons:
            p.use_smooth = smooth

    def paint_cells(cells_visual):
        self = MazeVisual
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

        random.seed(self.props.seed_color)

        rand = random.random
        groups = set()
        group_colors = {}
        for c in linked_cells:
            groups.add(c.group)
        for g in groups:
            group_colors[g] = rand(), rand(), rand(), 1

        neighbors_colors = {}
        for n in [i for i in range(10)]:
            neighbors_colors[n] = (rand(), rand(), rand(), 1)

        for cv in cells_visual:
            c = cv.cell
            this_distance = distances[c]
            relative_distance = 0 if this_distance is None else this_distance / max_distance
            new_col = (relative_distance, 0 if c in longest_path else 1, 0, 0 if this_distance is not None else 1)
            cv.color_layers[DISTANCE] = new_col

            cv.color_layers[GROUP] = group_colors[c.group]

            cv.color_layers[NEIGHBORS] = neighbors_colors[len(c.links)]

            for f in cv.faces:
                f.set_vertex_group(VG_STAIRS, [relative_distance] * f.corners())
                f.set_wall_vertex_groups(VG_STAIRS, [relative_distance] * f.wall_vertices())

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
    cell_sep_rgb_node = None
    cell_bsdf_node = None
    cell_output_node = None

    def get_or_create_node(nodes, name, type, pos=None):
        node = nodes.get(name, nodes.new(type=type))
        node.name = name
        if pos:
            node.location = pos
        return node

    def init_cell_rgb_node(nodes, props):
        MaterialManager.cell_rgb_node = MaterialManager.get_or_create_node(nodes, 'rgb', 'ShaderNodeRGB', (-400, -300))
        random.seed(props.seed_color)
        MaterialManager.cell_rgb_node.outputs['Color'].default_value = (random.random(), random.random(), random.random(), 1)

    def init_cell_vertex_colors_node(nodes, props):
        MaterialManager.cell_vertex_colors_node = MaterialManager.get_or_create_node(nodes, 'vertex_colors', 'ShaderNodeVertexColor', (-1200, 0))
        MaterialManager.cell_vertex_colors_node.layer_name = props.paint_style

    def init_cell_hsv_node(nodes, scene):
        MaterialManager.cell_hsv_node = MaterialManager.get_or_create_node(nodes, 'hsv', 'ShaderNodeHueSaturation', (-200, 0))

    def init_cell_bsdf_node(nodes):
        MaterialManager.cell_bsdf_node = MaterialManager.get_or_create_node(nodes, 'bsdf', 'ShaderNodeBsdfPrincipled')

    def init_cell_sep_rgb_node(nodes):
        MaterialManager.cell_sep_rgb_node = MaterialManager.get_or_create_node(nodes, 'sep_rgb', 'ShaderNodeSeparateRGB', (-1000, 0))

    def init_cell_mix_distance_node(nodes, props):
        MaterialManager.cell_cr_distance_node = nodes.get('cr_distance', nodes.new(type='ShaderNodeValToRGB'))
        if MaterialManager.cell_cr_distance_node.name != 'cr_distance':
            MaterialManager.cell_cr_distance_node.name = 'cr_distance'
            MaterialManager.cell_cr_distance_node.color_ramp.elements[0].color = (0, 1, 0, 1)
            MaterialManager.cell_cr_distance_node.color_ramp.elements[1].color = [1, 0, 0, 1]
        MaterialManager.cell_cr_distance_node.location = -800, -100

    def init_cell_math_node(nodes, props):
        MaterialManager.cell_math_node = MaterialManager.get_or_create_node(nodes, 'math_node', 'ShaderNodeMath', (-800, 100))
        MaterialManager.cell_math_node.operation = 'MULTIPLY'
        MaterialManager.cell_math_node.inputs[1].default_value = props.show_only_longest_path

    def init_cell_math_alpha_node(nodes):
        MaterialManager.cell_math_alpha_node = MaterialManager.get_or_create_node(nodes, 'math_alpha', 'ShaderNodeMath', (-800, 300))
        MaterialManager.cell_math_alpha_node.operation = 'ADD'

    def init_cell_value_node(nodes):
        MaterialManager.cell_value_node = MaterialManager.get_or_create_node(nodes, 'value', 'ShaderNodeValue', (-1000, -400))

    def init_cell_mix_under_node(nodes):
        MaterialManager.cell_mix_under_node = MaterialManager.get_or_create_node(nodes, 'mix_under', 'ShaderNodeMixRGB', (-800, -400))
        MaterialManager.cell_mix_under_node.blend_type = 'SUBTRACT'
        MaterialManager.cell_mix_under_node.inputs[0].default_value = 0.5

    def init_cell_mix_longest_distance_node(nodes):
        MaterialManager.cell_mix_longest_distance_node = MaterialManager.get_or_create_node(nodes, 'mix_longest_distance', 'ShaderNodeMixRGB', (-400, 0))
        MaterialManager.cell_mix_longest_distance_node.inputs[2].default_value = [0.5, 0.5, 0.5, 1]

    def init_cell_output_node(nodes):
        MaterialManager.cell_output_node = MaterialManager.get_or_create_node(nodes, 'output', 'ShaderNodeOutputMaterial', (300, 0))

    @staticmethod
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

        self.init_cell_rgb_node(nodes, props)
        self.init_cell_vertex_colors_node(nodes, props)
        self.init_cell_hsv_node(nodes, scene)
        self.init_cell_sep_rgb_node(nodes)
        self.init_cell_mix_distance_node(nodes, props)
        self.init_cell_math_node(nodes, props)
        self.init_cell_math_alpha_node(nodes)
        self.init_cell_value_node(nodes)
        self.init_cell_mix_under_node(nodes)
        self.init_cell_mix_longest_distance_node(nodes)
        self.init_cell_bsdf_node(nodes)
        self.init_cell_output_node(nodes)

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
            else:  # Neighbors.
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
        if MazeVisual.props.auto_overwrite:
            vertex_colors.outputs['Color'].default_value = [0, 0, 0, 1]

        principled = nodes.new(type='ShaderNodeBsdfPrincipled')

        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = 300, 0

        links = mat.node_tree.links
        links.new(vertex_colors.outputs[0], principled.inputs[0])
        links.new(principled.outputs[0], output.inputs[0])
