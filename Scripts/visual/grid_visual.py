import bpy
from mathutils import Color
from random import seed, random
from .. utils . modifier_manager import add_modifier, add_driver_to_object
from .. utils . distance_manager import Distances
from .. utils . vertex_colors_manager import set_vertex_color_layers
from .. maze_logic . data_structure . grid import Grid
from .. maze_logic . data_structure . grid_polar import GridPolar
from .. maze_logic . data_structure . grid_hex import GridHex
from .. maze_logic . data_structure . grid_triangle import GridTriangle
from .. maze_logic . algorithms import algorithm_manager
from .. visual . cell_type_manager import POLAR, TRIANGLE, HEXAGON, get_cell_vertices


DISTANCE = 'DISTANCE'
GROUP = 'GROUP'
NEIGHBORS = 'NEIGHBORS'


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

        self.generate_grid()
        algorithm_manager.work(props.maze_algorithm, self.grid, props.seed, max_steps=props.steps)
        self.grid.braid_dead_ends(props.braid_dead_ends, props.seed)
        self.generate_objects()
        self.build_objects()
        self.generate_modifiers()
        self.generate_drivers()
        self.set_materials()
        self.paint_cells()
        self.offset_objects()

        GridVisual.Instance = self

    def generate_grid(self):
        props = self.props
        if props.cell_type == POLAR:
            g = GridPolar(props.rows_or_radius)
        elif props.cell_type == HEXAGON:
            g = GridHex(props.rows_or_radius, props.rows_or_radius)
        elif props.cell_type == TRIANGLE:
            g = GridTriangle(props.rows_or_radius, props.rows_or_radius)
        else:
            g = Grid(props.rows_or_radius, props.rows_or_radius)
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

    def set_materials(self):
        try:
            mat = self.obj_cells.material_slots[0].material
        except IndexError:
            mat = bpy.data.materials.new("mat_cells")
            self.obj_cells.data.materials.append(mat)
        mat.use_nodes = True

        nodes = mat.node_tree.nodes
        nodes.clear()
        if self.props.paint_style == 'UNIFORM':
            color_node = nodes.new(type='ShaderNodeRGB')
            color_node.location = -400, 0
            seed(self.props.seed_color)
            color_node.outputs['Color'].default_value = (random(), random(), random(), 1)
        else:
            color_node = nodes.new(type='ShaderNodeVertexColor')
            color_node.layer_name = self.props.paint_style

        color_node.location = -400, 0
        hue_sat_value = nodes.new(type='ShaderNodeHueSaturation')        
        hue_sat_value.location = -200, 0
        add_driver_to_object(hue_sat_value.inputs['Hue'], 'default_value', 'hue_shift', 'SCENE', self.scene, 'mg_props.hue_shift', '0.5 + hue_shift')
        add_driver_to_object(hue_sat_value.inputs['Saturation'], 'default_value', 'sat_shift', 'SCENE', self.scene, 'mg_props.saturation_shift', '1 + sat_shift')
        add_driver_to_object(hue_sat_value.inputs['Value'], 'default_value', 'val_shift', 'SCENE', self.scene, 'mg_props.value_shift', '1 + val_shift')

        principled = nodes.new(type='ShaderNodeBsdfPrincipled')

        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = 300, 0

        links = mat.node_tree.links
        links.new(color_node.outputs[0], hue_sat_value.inputs[4])
        links.new(hue_sat_value.outputs[0], principled.inputs[0])
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
        all_walls, all_cells = self.grid.get_blueprint()        

        self.mesh_wall.from_pydata(
            all_walls,
            [(i, i + 1) for i in range(0, len(all_walls) - 1, 2)],
            [])
        edges = []
        cell_vertices = self.cell_vertices
        # Connect all cell edges to make a face:
        for cv in range(cell_vertices):
            edges.extend([(i + cv, i + (1 + cv) % (cell_vertices)) for i in range(0, len(all_cells) - (1 + cv), cell_vertices)])

        faces = []
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

    def paint_cells(self):
        layers = {DISTANCE: [], GROUP: [], NEIGHBORS: []}

        unmasked_and_linked_cells = self.grid.get_unmasked_and_linked_cells()

        distances = Distances(self.grid.get_random_unmasked_and_linked_cell(_seed=self.props.seed))
        distances.get_distances()
        new_start, distance = distances.max()
        distances = Distances(new_start)
        distances.get_distances()
        goal, max_distance = distances.max()

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
            if this_distance is not None:  # Do not simplify "if this_distance is not None" to "if this_distance"
                relative_distance = this_distance / max_distance
                new_col = Color((relative_distance, 1 - relative_distance, 0))
                layers[DISTANCE].append((new_col.r, new_col.g, new_col.b, 1))
            else:
                layers[DISTANCE].append((0.5, 0.5, 0.5, 1))

            layers[GROUP].append(group_colors[c.group])

            layers[NEIGHBORS].append(neighbors_colors[len(c.links)])

        set_vertex_color_layers(self.obj_cells, layers, self.cell_vertices)
