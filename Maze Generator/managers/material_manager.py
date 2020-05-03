import bpy
import random
from typing import Iterable
from . import object_manager
from ..managers import mesh_manager


def get_or_create_node(
        nodes: bpy.types.Nodes,
        node_attr_name: str,
        _type: str,
        pos: Iterable[float] = None,
        inputs: dict = None,  # Index (integer or string), value
        outputs: dict = None,  # Index (integer or string), value
        attributes: dict = None) -> None:
    node = nodes.get(node_attr_name)
    if not node:
        node = nodes.new(type=_type)
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


class MaterialManager:

    @staticmethod
    def set_materials(props, scene) -> None:
        MaterialManager.set_cell_material(props, scene)
        MaterialManager.set_cell_contour_material(props)
        MaterialManager.set_wall_material(props)

    def set_cell_material(props, scene) -> None:
        self = MaterialManager
        already_created = False
        obj_cells = object_manager.ObjectManager.obj_cells

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

        random.seed(props.seed_color)
        get_or_create_node(
            nodes, 'cell_rgb_node', 'ShaderNodeRGB', (-400, -300))
        get_or_create_node(
            nodes, 'cell_vertex_colors_distance_node', 'ShaderNodeVertexColor', (-1400, 0),
            attributes={'layer_name': mesh_manager.DISTANCE})
        get_or_create_node(
            nodes, 'cell_vertex_colors_neighbors_node', 'ShaderNodeVertexColor', (-1400, 200),
            attributes={'layer_name': mesh_manager.NEIGHBORS})
        get_or_create_node(
            nodes, 'cell_vertex_colors_group_node', 'ShaderNodeVertexColor', (-1400, -200),
            attributes={'layer_name': mesh_manager.GROUP})
        get_or_create_node(nodes, 'cell_hsv_node', 'ShaderNodeHueSaturation', (-200, 0))
        get_or_create_node(nodes, 'cell_sep_rgb_node', 'ShaderNodeSeparateRGB', (-1200, 0))

        get_or_create_node(nodes, 'cell_cr_distance_node', 'ShaderNodeValToRGB', (-800, -100))
        try:
            MaterialManager.cell_cr_distance_node.color_ramp.elements[0].color = (0, 1, 0, 1)
            MaterialManager.cell_cr_distance_node.color_ramp.elements[1].color = (1, 0, 0, 1)
        except IndexError:
            pass

        get_or_create_node(
            nodes, 'cell_math_node', 'ShaderNodeMath', (-800, 100),
            inputs={1: props.show_longest_path},
            attributes={'operation': 'MULTIPLY'})
        get_or_create_node(
            nodes, 'cell_math_alpha_node', 'ShaderNodeMath', (-800, 300),
            attributes={'operation': 'ADD'})
        get_or_create_node(
            nodes, 'cell_mix_longest_distance_node', 'ShaderNodeMixRGB', (-400, 0),
            inputs={2: (0.5, 0.5, 0.5, 1)})
        get_or_create_node(nodes, 'cell_bsdf_node', 'ShaderNodeBsdfPrincipled')
        get_or_create_node(nodes, 'cell_output_node', 'ShaderNodeOutputMaterial', (300, 0))

        get_or_create_node(
            nodes, 'cell_math_compare_node', 'ShaderNodeMath', (-1000, 200),
            inputs={1: 0},
            attributes={'operation': 'COMPARE'})

        links = mat.node_tree.links
        links.new(self.cell_sep_rgb_node.outputs[0], self.cell_cr_distance_node.inputs[0])
        links.new(self.cell_sep_rgb_node.outputs[1], self.cell_math_node.inputs[0])
        links.new(self.cell_sep_rgb_node.outputs[0], self.cell_math_compare_node.inputs[0])
        links.new(self.cell_math_compare_node.outputs[0], self.cell_math_alpha_node.inputs[1])

        links.new(self.cell_math_node.outputs[0], self.cell_math_alpha_node.inputs[0])
        links.new(self.cell_math_alpha_node.outputs[0], self.cell_mix_longest_distance_node.inputs[0])

        links.new(self.cell_cr_distance_node.outputs[0], self.cell_mix_longest_distance_node.inputs[1])
        links.new(self.cell_mix_longest_distance_node.outputs[0], self.cell_hsv_node.inputs[4])
        if props.paint_style == mesh_manager.DISTANCE:
            links.new(self.cell_vertex_colors_distance_node.outputs[0], self.cell_sep_rgb_node.inputs[0])
        elif props.paint_style == mesh_manager.UNIFORM:
            links.new(self.cell_rgb_node.outputs[0], self.cell_mix_longest_distance_node.inputs[1])
        elif props.paint_style == mesh_manager.GROUP:
            links.new(self.cell_vertex_colors_group_node.outputs[0], self.cell_cr_distance_node.inputs[0])
        else:  # Neighbors.
            links.new(self.cell_vertex_colors_neighbors_node.outputs[0], self.cell_cr_distance_node.inputs[0])

        links.new(self.cell_hsv_node.outputs[0], self.cell_bsdf_node.inputs[0])
        links.new(self.cell_bsdf_node.outputs[0], self.cell_output_node.inputs[0])

    def set_cell_contour_material(props) -> None:
        obj_cells = object_manager.ObjectManager.obj_cells
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

    def set_wall_material(props) -> None:
        obj_walls = object_manager.ObjectManager.obj_walls
        try:
            mat = obj_walls.material_slots[0].material
            if not props.auto_overwrite:
                MaterialManager.wall_principled = mat.node_tree.nodes['Principled BSDF']
                return
        except IndexError:
            mat = bpy.data.materials.new("mat_walls")
            obj_walls.data.materials.append(mat)
            mat.use_nodes = True

        MaterialManager.wall_principled = mat.node_tree.nodes['Principled BSDF']
        MaterialManager.wall_principled.inputs[0].default_value = (0, 0, 0, 1)
