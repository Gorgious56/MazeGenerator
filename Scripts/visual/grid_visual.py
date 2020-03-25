import bpy
from random import seed, random
from .. utils . modifier_manager import add_modifier, add_driver_to, WALL_BEVEL_NAME, WALL_WELD_NAME, WALL_SCREW_NAME, WALL_SOLIDIFY_NAME, CELL_SOLIDIFY_NAME, \
    CELL_WELD_NAME, CELL_DECIMATE_NAME, CELL_BEVEL_NAME
from .. utils . distance_manager import Distances
from .. utils . mesh_manager import set_mesh_layers
from .. maze_logic . data_structure . grids . grid import Grid
from .. maze_logic . data_structure . grids . grid_polar import GridPolar
from .. maze_logic . data_structure . grids . grid_hex import GridHex
from .. maze_logic . data_structure . grids . grid_triangle import GridTriangle
from .. maze_logic . data_structure . grids . grid_weave import GridWeave
from .. maze_logic . data_structure . cells . cell_under import CellUnder
from .. maze_logic . algorithms import algorithm_manager
from .. visual . cell_type_manager import POLAR, TRIANGLE, HEXAGON, get_cell_vertices
from .. visual . cell_visual_manager import DISTANCE, GROUP, NEIGHBORS, UNIFORM


class GridVisual:
    Instance = None

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
        self.set_materials()
        self.paint_cells()
        self.offset_objects()
        self.update_visibility()

        GridVisual.Instance = self

    def update_visibility(self):
        set_hidden = self.props.wall_hide and self.props.cell_inset > 0 or self.props.maze_weave
        self.obj_walls.hide_viewport = set_hidden
        self.obj_walls.hide_render = set_hidden

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
                self.grid = GridWeave(rows=props.rows_or_radius, columns=props.rows_or_radius, cell_size=1 - max(0.1, props.cell_inset), cell_thickness=props.cell_thickness)
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

    def set_cell_material(self):
        try:
            mat = self.obj_cells.material_slots[0].material
        except IndexError:
            mat = bpy.data.materials.new("mat_cells")
            self.obj_cells.data.materials.append(mat)
        mat.use_nodes = True

        nodes = mat.node_tree.nodes
        nodes.clear()
        if self.props.paint_style == UNIFORM:
            color_node = nodes.new(type='ShaderNodeRGB')
            color_node.location = -400, 0
            seed(self.props.seed_color)
            color_node.outputs['Color'].default_value = (random(), random(), random(), 1)
        else:
            color_node = nodes.new(type='ShaderNodeVertexColor')
            color_node.layer_name = self.props.paint_style

        hue_sat_value = nodes.new(type='ShaderNodeHueSaturation')
        hue_sat_value.location = -200, 0
        add_driver_to(hue_sat_value.inputs['Hue'], 'default_value', 'hue_shift', 'SCENE', self.scene, 'mg_props.hue_shift', '0.5 + hue_shift')
        add_driver_to(hue_sat_value.inputs['Saturation'], 'default_value', 'sat_shift', 'SCENE', self.scene, 'mg_props.saturation_shift', '1 + sat_shift')
        add_driver_to(hue_sat_value.inputs['Value'], 'default_value', 'val_shift', 'SCENE', self.scene, 'mg_props.value_shift', '1 + val_shift')

        principled = nodes.new(type='ShaderNodeBsdfPrincipled')

        if self.props.paint_style == DISTANCE:
            color_node.location = -1000, 0

            sep_rgb = nodes.new(type='ShaderNodeSeparateRGB')
            sep_rgb.location = -800, 0

            mix_rgb_1 = nodes.new(type='ShaderNodeMixRGB')
            start_color, end_color = self.props.distance_color_start, self.props.distance_color_end
            mix_rgb_1.inputs[1].default_value = [start_color[0], start_color[1], start_color[2], 1]
            mix_rgb_1.inputs[2].default_value = [end_color[0], end_color[1], end_color[2], 1]
            mix_rgb_1.location = -600, -100

            math_node = nodes.new(type='ShaderNodeMath')
            math_node.operation = 'MULTIPLY'
            math_node.inputs[1].default_value = self.props.show_only_longest_path
            math_node.location = -600, 100

            value_node = nodes.new(type='ShaderNodeValue')
            value_node.location = -800, -300

            mix_rgb_3 = nodes.new(type='ShaderNodeMixRGB')
            mix_rgb_3.blend_type = 'SUBTRACT'
            mix_rgb_3.inputs[0].default_value = 0.5
            mix_rgb_3.location = -600, -300

            mix_rgb_2 = nodes.new(type='ShaderNodeMixRGB')
            mix_rgb_2.inputs[2].default_value = [0.5, 0.5, 0.5, 1]
            mix_rgb_2.location = -400, 0

            output = nodes.new(type='ShaderNodeOutputMaterial')
            output.location = 300, 0

            links = mat.node_tree.links
            links.new(color_node.outputs[0], sep_rgb.inputs[0])
            links.new(sep_rgb.outputs[0], mix_rgb_1.inputs[0])
            links.new(sep_rgb.outputs[1], math_node.inputs[0])
            links.new(value_node.outputs[0], mix_rgb_3.inputs[1])
            links.new(sep_rgb.outputs[2], mix_rgb_3.inputs[2])
            links.new(mix_rgb_3.outputs[0], hue_sat_value.inputs[2])
            links.new(math_node.outputs[0], mix_rgb_2.inputs[0])
            links.new(mix_rgb_1.outputs[0], mix_rgb_2.inputs[1])
            links.new(mix_rgb_2.outputs[0], hue_sat_value.inputs[4])
            
            add_driver_to(value_node.outputs[0], 'default_value', 'val_shift', 'SCENE', self.scene, 'mg_props.value_shift', '1 + val_shift')
            add_driver_to(mix_rgb_3.inputs[0], 'default_value', 'val_shift', 'SCENE', self.scene, 'mg_props.value_shift', '(val_shift + 1)/2')
        else:
            color_node.location = -400, 0

            output = nodes.new(type='ShaderNodeOutputMaterial')
            output.location = 300, 0

            links = mat.node_tree.links
            links.new(color_node.outputs[0], hue_sat_value.inputs[4])
        links.new(hue_sat_value.outputs[0], principled.inputs[0])
        links.new(principled.outputs[0], output.inputs[0])

    def set_cell_contour_material(self):
        try:
            mat = self.obj_cells.material_slots[1].material
        except IndexError:
            mat = bpy.data.materials.new("mat_cells_contour")
            self.obj_cells.data.materials.append(mat)
        mat.use_nodes = True

        mat.node_tree.nodes['Principled BSDF'].inputs[0].default_value = (0, 0, 0, 1)
        mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 1

    def set_wall_material(self):
        try:
            mat = self.obj_walls.material_slots[0].material
        except IndexError:
            mat = bpy.data.materials.new("mat_walls")
            self.obj_walls.data.materials.append(mat)
        mat.use_nodes = True

        nodes = mat.node_tree.nodes
        nodes.clear()

        color_node = nodes.new(type='ShaderNodeRGB')
        color_node.location = -400, 0
        color = self.props.wall_color
        color_node.outputs['Color'].default_value = [color[0], color[1], color[2], 1]

        principled = nodes.new(type='ShaderNodeBsdfPrincipled')

        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = 300, 0

        links = mat.node_tree.links
        links.new(color_node.outputs[0], principled.inputs[0])
        links.new(principled.outputs[0], output.inputs[0])

    def set_materials(self):
        self.set_cell_material()
        self.set_cell_contour_material()
        self.set_wall_material()

    def generate_modifiers(self):
        props = self.props
        self.obj_walls.modifiers.clear()
        add_modifier(self.obj_walls, 'WELD', WALL_WELD_NAME, properties={'show_expanded': False})
        add_modifier(self.obj_walls, 'SCREW', WALL_SCREW_NAME, properties={'show_expanded': False, 'angle': 0, 'steps': 2, 'render_steps': 2, 'screw_offset': props.wall_height})
        add_modifier(self.obj_walls, 'SOLIDIFY', WALL_SOLIDIFY_NAME, properties={'show_expanded': False, 'solidify_mode': 'NON_MANIFOLD', 'thickness': props.wall_width, 'offset': 0})
        add_modifier(self.obj_walls, 'BEVEL', WALL_BEVEL_NAME, properties={'show_expanded': False, 'segments': 4, 'limit_method': 'ANGLE'})

        self.obj_cells.modifiers.clear()
        add_modifier(self.obj_cells, 'WELD', CELL_WELD_NAME, properties={'show_expanded': False})
        add_modifier(self.obj_cells, 'DECIMATE', CELL_DECIMATE_NAME, properties={'show_expanded': False, 'decimate_type': 'DISSOLVE'})
        add_modifier(self.obj_cells, 'SOLIDIFY', CELL_SOLIDIFY_NAME, properties={'show_expanded': False, 'use_even_offset': True})
        add_modifier(self.obj_cells, 'BEVEL', CELL_BEVEL_NAME, properties={'show_expanded': False, 'segments': 2, 'limit_method': 'ANGLE', 'material': 1, 'profile': 1, 'angle_limit': 1.5, 'use_clamp_overlap': False})

    def generate_drivers(self):
        add_driver_to(self.obj_walls.modifiers[WALL_SCREW_NAME], 'screw_offset', 'wall_height', 'SCENE', self.scene, 'mg_props.wall_height')
        add_driver_to(self.obj_walls.modifiers[WALL_SCREW_NAME], 'use_smooth_shade', 'wall_bevel', 'SCENE', self.scene, 'mg_props.wall_bevel', expression='wall_bevel > .005')
        add_driver_to(self.obj_walls.modifiers[WALL_SOLIDIFY_NAME], 'thickness', 'wall_thickness', 'SCENE', self.scene, 'mg_props.wall_width')
        add_driver_to(self.obj_walls.modifiers[WALL_BEVEL_NAME], 'width', 'wall_bevel', 'SCENE', self.scene, 'mg_props.wall_bevel')

        add_driver_to(self.obj_cells.modifiers[CELL_SOLIDIFY_NAME], 'thickness', 'cell_thickness', 'SCENE', self.scene, 'mg_props.cell_thickness')
        add_driver_to(self.obj_cells.modifiers[CELL_BEVEL_NAME], 'width', 'cell_contour', 'SCENE', self.scene, 'mg_props.cell_contour')

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

    def paint_cells(self):
        layers = {DISTANCE: [], GROUP: [], NEIGHBORS: []}

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
            new_col = (this_distance / max_distance if this_distance else 0, 0 if c in longest_path else 1, 1 if type(c) is CellUnder else 0, 1)
            cv.color_layers[DISTANCE] = new_col

            cv.color_layers[GROUP] = group_colors[c.group]

            cv.color_layers[NEIGHBORS] = neighbors_colors[len(c.links)]

        set_mesh_layers(self.obj_cells, self.cells_visual)

        # for c in unmasked_and_linked_cells:
        #     this_distance = distances[c]
        #     new_col = (this_distance / max_distance if this_distance else 0, 0 if c in longest_path else 1, 1 if type(c) is CellUnder else 0, 1)
        #     layers[DISTANCE].append(new_col)

        #     layers[GROUP].append(group_colors[c.group])

        #     layers[NEIGHBORS].append(neighbors_colors[len(c.links)])

        # set_vertex_color_layers(self.obj_cells, layers, self.cells_vertices if len(self.cells_vertices) > 0 else self.cell_vertices)
