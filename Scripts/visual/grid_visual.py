import bpy
from random import seed, random
from .. utils . modifier_manager import add_modifier, add_driver_to_object
from .. utils . distance_manager import Distances
from .. utils . mesh_manager import set_vertex_color_layers
from .. maze_logic . data_structure . grids . grid import Grid
from .. maze_logic . data_structure . grids . grid_polar import GridPolar
from .. maze_logic . data_structure . grids . grid_hex import GridHex
from .. maze_logic . data_structure . grids . grid_triangle import GridTriangle
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
        set_hidden = self.props.wall_hide and self.props.cell_size < 1
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
            grid = Grid
        g = grid(props.rows_or_radius, props.rows_or_radius, cell_size=props.cell_size)
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

    def set_materials(self):
        # Cells shader :
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
        add_driver_to_object(hue_sat_value.inputs['Hue'], 'default_value', 'hue_shift', 'SCENE', self.scene, 'mg_props.hue_shift', '0.5 + hue_shift')
        add_driver_to_object(hue_sat_value.inputs['Saturation'], 'default_value', 'sat_shift', 'SCENE', self.scene, 'mg_props.saturation_shift', '1 + sat_shift')
        add_driver_to_object(hue_sat_value.inputs['Value'], 'default_value', 'val_shift', 'SCENE', self.scene, 'mg_props.value_shift', '1 + val_shift')

        principled = nodes.new(type='ShaderNodeBsdfPrincipled')

        if self.props.paint_style == DISTANCE:
            color_node.location = -1000, 0

            sep_rgb = nodes.new(type='ShaderNodeSeparateRGB')
            sep_rgb.location = -800, 0

            mix_rgb_1 = nodes.new(type='ShaderNodeMixRGB')
            start_color, end_color = self.props.distance_color_start, self.props.distance_color_end
            mix_rgb_1.inputs[1].default_value = [start_color[0], start_color[1], start_color[2], 1]
            mix_rgb_1.inputs[2].default_value = [end_color[0], end_color[1], end_color[2], 1]
            mix_rgb_1.location = -600, 100

            math_node = nodes.new(type='ShaderNodeMath')
            math_node.operation = 'MULTIPLY'
            math_node.inputs[1].default_value = self.props.show_only_longest_path
            math_node.location = -600, -100

            mix_rgb_2 = nodes.new(type='ShaderNodeMixRGB')
            mix_rgb_2.inputs[2].default_value = [0.5, 0.5, 0.5, 1]
            mix_rgb_2.location = -400, 0

            output = nodes.new(type='ShaderNodeOutputMaterial')
            output.location = 300, 0

            links = mat.node_tree.links
            links.new(color_node.outputs[0], sep_rgb.inputs[0])
            links.new(sep_rgb.outputs[0], mix_rgb_1.inputs[0])
            links.new(sep_rgb.outputs[1], math_node.inputs[0])
            links.new(math_node.outputs[0], mix_rgb_2.inputs[0])
            links.new(mix_rgb_1.outputs[0], mix_rgb_2.inputs[1])
            links.new(mix_rgb_2.outputs[0], hue_sat_value.inputs[4])
        else:
            color_node.location = -400, 0

            output = nodes.new(type='ShaderNodeOutputMaterial')
            output.location = 300, 0

            links = mat.node_tree.links
            links.new(color_node.outputs[0], hue_sat_value.inputs[4])
        links.new(hue_sat_value.outputs[0], principled.inputs[0])
        links.new(principled.outputs[0], output.inputs[0])

        # Wall shader :
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

    def generate_modifiers(self):
        props = self.props
        self.obj_walls.modifiers.clear()
        add_modifier(self.obj_walls, 'WELD', 'Weld')
        add_modifier(self.obj_walls, 'SCREW', 'Screw', properties={'angle': 0, 'steps': 2, 'render_steps': 2, 'screw_offset': props.wall_height, 'use_smooth_shade': False})
        add_modifier(self.obj_walls, 'SOLIDIFY', 'Solidify', properties={'solidify_mode': 'NON_MANIFOLD', 'thickness': props.wall_width, 'offset': 0})

    def generate_drivers(self):
        add_driver_to_object(self.obj_walls.modifiers['Screw'], 'screw_offset', 'wall_height', 'SCENE', self.scene, 'mg_props.wall_height')
        add_driver_to_object(self.obj_walls.modifiers['Solidify'], 'thickness', 'wall_thickness', 'SCENE', self.scene, 'mg_props.wall_width')

    def offset_objects(self):
        if self.props.cell_type == POLAR:
            self.obj_walls.location.xyz = self.obj_cells.location.xyz = (0, 0, 0)
        elif self.props.cell_type == TRIANGLE:
            self.obj_walls.location.xyz = self.obj_cells.location.xyz = (-self.grid.columns / 4, -self.grid.rows / 2 + 0.5, 0)
        else:
            self.obj_walls.location.xyz = self.obj_cells.location.xyz = (-self.grid.columns / 2, -self.grid.rows / 2, 0)

    def build_objects(self):
        self.cells_vertices = []
        try:
            all_walls, all_cells, self.cells_vertices = self.grid.get_blueprint()
        except ValueError:
            all_walls, all_cells = self.grid.get_blueprint()

        self.mesh_wall.from_pydata(
            all_walls,
            [(i, i + 1) for i in range(0, len(all_walls) - 1, 2)],
            [])

        edges = []
        faces = []
        if len(self.cells_vertices) == 0:
            cell_vertices = self.cell_vertices
            # Connect all cell edges to make a face:
            for cv in range(cell_vertices):
                edges.extend([(i + cv, i + (1 + cv) % (cell_vertices)) for i in range(0, len(all_cells) - (1 + cv), cell_vertices)])

            for c in range(0, len(all_cells) - (cell_vertices - 1), cell_vertices):
                new_face = []
                for cv in range(cell_vertices):
                    new_face.append(c + cv)
                faces.append(new_face)

            self.mesh_cells.from_pydata(
                all_cells,
                edges,
                faces
            )
        else:
            current_index = 0
            for cv in self.cells_vertices:
                cell_start_index = current_index
                new_face = []
                for cell_index in range(cv):
                    next_index = current_index + 1
                    edges.extend([(current_index, next_index if next_index < cell_start_index + cv else cell_start_index)])
                    new_face.append(current_index)
                    current_index += 1
                faces.append(new_face)

            self.mesh_cells.from_pydata(
                all_cells,
                edges,
                faces
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

        for c in unmasked_and_linked_cells:
            this_distance = distances[c]
            layers[DISTANCE].append((this_distance / max_distance if this_distance else 0, 0 if c in longest_path else 1, 0, 1))

            layers[GROUP].append(group_colors[c.group])

            layers[NEIGHBORS].append(neighbors_colors[len(c.links)])

        set_vertex_color_layers(self.obj_cells, layers, self.cells_vertices if len(self.cells_vertices) > 0 else self.cell_vertices)
