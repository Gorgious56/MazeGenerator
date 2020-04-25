import bpy
import random
from typing import Iterable
from ..managers import modifier_manager as mod_mgr
from ..managers.distance_manager import Distances
from ..managers.mesh_manager import MeshManager
from ..managers.object_manager import ObjectManager
from ..managers.grid_manager import GridManager
from ..managers import algorithm_manager
from ..managers.cell_type_manager import POLAR, SQUARE, TRIANGLE, HEXAGON
from ..managers import space_rep_manager as sp_rep
from ..maze_logic import grids
from ..visual.cell_visual import DISTANCE, GROUP, NEIGHBORS, VG_DISPLACE, VG_STAIRS, UNIFORM, CellVisual


class MazeVisual:
    Mat_mgr = None
    tex_disp = None
    # grid = None
    scene = None
    props = None

    def refresh_maze(scene: bpy.types.Scene) -> None:
        MazeVisual.scene = scene
        MazeVisual.props = scene.mg_props
        ObjectManager.generate_objects(scene)
        MazeVisual.generate_textures()
        MaterialManager.set_materials()
        MeshManager.create_vertex_groups(ObjectManager.obj_cells, ObjectManager.obj_walls)
        mod_mgr.setup_modifiers_and_drivers(MazeVisual, ObjectManager)

    def generate_maze(scene: bpy.types.Scene) -> None:
        self = MazeVisual
        self.scene = scene
        self.props = scene.mg_props
        props = self.props

        GridManager.generate_grid(self.props)
        if not algorithm_manager.is_algo_incompatible(props):
            algorithm_manager.work(GridManager.grid, props)
            GridManager.grid.sparse_dead_ends(props.sparse_dead_ends, props.seed)
            props.dead_ends = GridManager.grid.braid_dead_ends(props.braid_dead_ends, props.seed)

            ObjectManager.generate_objects(scene)
            ObjectManager.update_wall_visibility(self.props, algorithm_manager.is_algo_weaved(self.props))
            self.generate_textures()
            self.build_objects()
            MeshManager.create_vertex_groups(ObjectManager.obj_cells, ObjectManager.obj_walls)
            mod_mgr.setup_modifiers_and_drivers(MazeVisual, ObjectManager)

            MaterialManager.set_materials()


    def generate_textures() -> None:
        self = MazeVisual
        tex_disp_name = 'MG_Tex_Disp'

        try:
            self.tex_disp = bpy.data.textures[tex_disp_name]
        except KeyError:
            self.tex_disp = bpy.data.textures.new(name=tex_disp_name, type='CLOUDS')
            self.tex_disp.noise_scale = 50
        self.tex_disp.cloud_type = 'COLOR'

    def build_objects() -> None:
        om = ObjectManager
        self = MazeVisual
        cells_visual = GridManager.grid.get_blueprint()

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

        om.mesh_wall.clear_geometry()
        om.mesh_wall.from_pydata(
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

        om.mesh_cells.clear_geometry()
        om.mesh_cells.from_pydata(
            cells_corners,
            [],
            cells_faces
        )

        if self.props.cell_use_smooth:  # Update only when the mesh is supposed to be smoothed, because the default will be unsmoothed
            self.update_cell_smooth()
        for mesh in (om.mesh_cells, om.mesh_wall):
            mesh.use_auto_smooth = True
            mesh.auto_smooth_angle = 0.5

        MazeVisual.paint_cells(cells_visual)

    @staticmethod
    def update_cell_smooth() -> None:
        smooth = MazeVisual.props.cell_use_smooth
        for p in MazeVisual.mesh_cells.polygons:
            p.use_smooth = smooth

    def paint_cells(cells_visual: Iterable[CellVisual]) -> None:
        self = MazeVisual
        om = ObjectManager
        linked_cells = GridManager.grid.get_linked_cells()

        distances = Distances(GridManager.grid.get_random_linked_cell(_seed=self.props.seed))
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

        MeshManager.set_mesh_layers(om.obj_cells, om.obj_walls, cells_visual, self.props)


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

    def get_or_create_node(
            nodes: bpy.types.Nodes,
            node_attr_name: str,
            _type: str,
            pos: Iterable[float] = None,
            inputs: dict = None,  # Index (integer or string), value
            outputs: dict = None,  # Index (integer or string), value
            attributes: dict = None) -> None:
        node = nodes.get(node_attr_name, nodes.new(type=_type))
        node.name = node_attr_name
        if pos:
            node.location = pos
        if inputs:
            for index, value in inputs.items():
                node.inputs[index].default_value = value
        if outputs:
            for index, value in outputs.items():
                node.outputs[index].default_value = value
        if attributes:
            for name, value in attributes.items():
                setattr(node, name, value)
        setattr(MaterialManager, node_attr_name, node)

    @staticmethod
    def set_materials() -> None:
        MaterialManager.set_cell_material()
        MaterialManager.set_cell_contour_material()
        MaterialManager.set_wall_material()

    def set_cell_material() -> None:
        self = MaterialManager
        already_created = False
        obj_cells = ObjectManager.obj_cells
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

        random.seed(MazeVisual.props.seed_color)
        MaterialManager.get_or_create_node(
            nodes, 'cell_rgb_node', 'ShaderNodeRGB', (-400, -300),
            outputs={'Color': (random.random(), random.random(), random.random(), 1)})
        MaterialManager.get_or_create_node(
            nodes, 'cell_vertex_colors_node', 'ShaderNodeVertexColor', (-1200, 0),
            attributes={'layer_name': MazeVisual.props.paint_style})
        MaterialManager.get_or_create_node(nodes, 'cell_hsv_node', 'ShaderNodeHueSaturation', (-200, 0))
        MaterialManager.get_or_create_node(nodes, 'cell_sep_rgb_node', 'ShaderNodeSeparateRGB', (-1000, 0))

        MaterialManager.cell_cr_distance_node = nodes.get('cell_cr_distance_node', nodes.new(type='ShaderNodeValToRGB'))
        if MaterialManager.cell_cr_distance_node.name != 'cell_cr_distance_node':
            MaterialManager.cell_cr_distance_node.name = 'cell_cr_distance_node'
            MaterialManager.cell_cr_distance_node.color_ramp.elements[0].color = (0, 1, 0, 1)
            MaterialManager.cell_cr_distance_node.color_ramp.elements[1].color = [1, 0, 0, 1]
        MaterialManager.cell_cr_distance_node.location = -800, -100

        MaterialManager.get_or_create_node(
            nodes, 'cell_math_node', 'ShaderNodeMath', (-800, 100),
            inputs={1: MazeVisual.props.show_only_longest_path},
            attributes={'operation': 'MULTIPLY'})
        MaterialManager.get_or_create_node(
            nodes, 'cell_math_alpha_node', 'ShaderNodeMath', (-800, 300),
            attributes={'operation': 'ADD'})
        MaterialManager.get_or_create_node(nodes, 'cell_value_node', 'ShaderNodeValue', (-1000, -400))
        MaterialManager.get_or_create_node(
            nodes, 'cell_mix_under_node', 'ShaderNodeMixRGB', (-800, -400),
            inputs={0: 0.5},
            attributes={'blend_type': 'SUBTRACT'})
        MaterialManager.get_or_create_node(
            nodes, 'cell_mix_longest_distance_node', 'ShaderNodeMixRGB', (-400, 0), 
            inputs={2: (0.5, 0.5, 0.5, 1)})
        MaterialManager.get_or_create_node(nodes, 'cell_bsdf_node', 'ShaderNodeBsdfPrincipled')
        MaterialManager.get_or_create_node(nodes, 'cell_output_node', 'ShaderNodeOutputMaterial', (300, 0))

        try:
            self.cell_vertex_colors_node.layer_name = props.paint_style
            links = mat.node_tree.links
            if props.paint_style == DISTANCE:
                links.new(self.cell_vertex_colors_node.outputs[0], self.cell_sep_rgb_node.inputs[0])
                links.new(self.cell_sep_rgb_node.outputs[0], self.cell_cr_distance_node.inputs[0])
                links.new(self.cell_sep_rgb_node.outputs[1], self.cell_math_node.inputs[0])
                links.new(self.cell_value_node.outputs[0], self.cell_mix_under_node.inputs[1])
                links.new(self.cell_sep_rgb_node.outputs[2], self.cell_mix_under_node.inputs[2])
                # links.new(self.cell_mix_under_node.outputs[0], self.cell_hsv_node.inputs[2])

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

        except (IndexError, AttributeError):
            pass

    def set_cell_contour_material() -> None:
        props = MazeVisual.props
        obj_cells = ObjectManager.obj_cells
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

    def set_wall_material() -> None:
        props = MazeVisual.props
        obj_walls = ObjectManager.obj_walls
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
