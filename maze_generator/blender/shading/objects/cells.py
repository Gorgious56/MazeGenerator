"""
Contains methods to access and modify the cells object material
"""


import random
import bpy
from ..nodes import create_node, node_from_mat
from ... import meshes as mesh_manager
from ...drivers.methods import setup_driver, DriverProperties, DriverVariable


def set_cell_materials(scene, props):
    __set_cell_material(props)
    __set_cell_contour_material(props)
    __set_drivers(scene, props)


def update_links(props):
    __link_cell_nodes(props)


def __set_cell_material(props) -> None:
    obj_cells = props.objects.cells
    try:
        mat = obj_cells.material_slots[0].material
        if not props.core.auto_overwrite:
            return
    except IndexError:
        mat = bpy.data.materials.new("mat_cells")
        obj_cells.data.materials.append(mat)
    mat.use_nodes = True
    mat.node_tree.nodes.clear()
    props.display.materials.cell = mat
    __create_cell_nodes(props)
    __link_cell_nodes(props)


def __set_cell_contour_material(props) -> None:
    obj_cells = props.objects.cells
    try:
        mat = obj_cells.material_slots[1].material
        if not props.core.auto_overwrite:
            return
    except IndexError:
        mat = bpy.data.materials.new("mat_cells_contour")
        obj_cells.data.materials.append(mat)
        mat.use_nodes = True

    for node in mat.node_tree.nodes:
        if isinstance(node, bpy.types.ShaderNodeBsdfPrincipled):
            node.inputs[0].default_value = (0, 0, 0, 1)
            node.inputs[7].default_value = 1
            break


def __create_cell_nodes(props):
    mat = props.display.materials.cell
    nodes = mat.node_tree.nodes
    # if not already_created or props.core.auto_overwrite:
    #     nodes.clear()
    #     mat.blend_method = 'HASHED'

    random.seed(props.display.seed_color)
    create_node(nodes, NodeNames.rgb, "ShaderNodeRGB", (-400, -300))
    create_node(
        nodes,
        NodeNames.vertex_colors_distance,
        "ShaderNodeVertexColor",
        (-1400, 0),
        attributes={"layer_name": mesh_manager.DISTANCE},
    )
    create_node(
        nodes,
        NodeNames.vertex_colors_neighbors,
        "ShaderNodeVertexColor",
        (-1400, 200),
        attributes={"layer_name": mesh_manager.NEIGHBORS},
    )
    create_node(
        nodes,
        NodeNames.vertex_colors_group,
        "ShaderNodeVertexColor",
        (-1400, -200),
        attributes={"layer_name": mesh_manager.GROUP},
    )
    create_node(nodes, NodeNames.hsv, "ShaderNodeHueSaturation", (-200, 0))
    create_node(nodes, NodeNames.sep_rgb, "ShaderNodeSeparateRGB", (-1200, 0))

    create_node(nodes, NodeNames.cr_distance, "ShaderNodeValToRGB", (-800, -100))
    # if not already_created or props.core.auto_overwrite:
    try:
        cr_distance = node_from_mat(mat, NodeNames.cr_distance)
        cr_distance.color_ramp.elements[0].color = (0, 1, 0, 1)
        cr_distance.color_ramp.elements[1].color = (1, 0, 0, 1)
    except IndexError:
        pass

    create_node(
        nodes,
        NodeNames.math,
        "ShaderNodeMath",
        (-800, 100),
        inputs={1: props.display.show_longest_path},
        attributes={"operation": "MULTIPLY"},
    )
    create_node(nodes, NodeNames.math_alpha, "ShaderNodeMath", (-800, 300), attributes={"operation": "ADD"})
    create_node(nodes, NodeNames.mix_longest_distance, "ShaderNodeMixRGB", (-400, 0), inputs={2: (0.5, 0.5, 0.5, 1)})
    create_node(nodes, NodeNames.bsdf, "ShaderNodeBsdfPrincipled")
    create_node(nodes, NodeNames.output, "ShaderNodeOutputMaterial", (300, 0))
    create_node(
        nodes,
        NodeNames.math_compare,
        "ShaderNodeMath",
        (-1000, 200),
        inputs={1: -0.01},
        attributes={"operation": "COMPARE"},
    )


def __set_drivers(scene, props):
    mat = props.display.materials.cell
    nodes = mat.node_tree.nodes

    show_longest_path_node = nodes.get(NodeNames.math)
    if show_longest_path_node:
        setup_driver(
            show_longest_path_node.inputs[1],
            DriverProperties(
                "default_value",
                DriverVariable("show_longest_path", "SCENE", scene, "mg_props.display.show_longest_path"),
                "show_longest_path",
            ),
        )


class NodeNames:
    """
    Stores the cell node names
    """

    rgb = "cell_rgb_node"
    vertex_colors_distance = "cell_vertex_colors_distance_node"
    vertex_colors_neighbors = "cell_vertex_colors_neighbors_node"
    vertex_colors_group = "cell_vertex_colors_group_node"
    hsv = "cell_hsv_node"
    sep_rgb = "cell_sep_rgb_node"
    cr_distance = "cell_cr_distance_node"
    math = "cell_math_node"
    math_alpha = "cell_math_alpha_node"
    mix_longest_distance = "cell_mix_longest_distance_node"
    math_compare = "cell_math_compare_node"
    bsdf = "cell_bsdf_node"
    output = "cell_output_node"


def __link_cell_nodes(props):
    mat = props.display.materials.cell
    links = mat.node_tree.links
    sep_rgb = node_from_mat(mat, NodeNames.sep_rgb)
    cr_distance = node_from_mat(mat, NodeNames.cr_distance)
    math = node_from_mat(mat, NodeNames.math)
    math_compare = node_from_mat(mat, NodeNames.math_compare)
    math_alpha = node_from_mat(mat, NodeNames.math_alpha)
    mix_longest_distance = node_from_mat(mat, NodeNames.mix_longest_distance)
    bsdf = node_from_mat(mat, NodeNames.bsdf)
    hsv = node_from_mat(mat, NodeNames.hsv)
    vertex_colors_distance = node_from_mat(mat, NodeNames.vertex_colors_distance)
    rgb = node_from_mat(mat, NodeNames.rgb)
    vertex_colors_group = node_from_mat(mat, NodeNames.vertex_colors_group)
    vertex_colors_neighbors = node_from_mat(mat, NodeNames.vertex_colors_neighbors)

    links.new(sep_rgb.outputs[0], cr_distance.inputs[0])
    links.new(sep_rgb.outputs[1], math.inputs[0])
    links.new(sep_rgb.outputs[0], math_compare.inputs[0])
    links.new(math_compare.outputs[0], math_alpha.inputs[1])

    links.new(math.outputs[0], math_alpha.inputs[0])
    links.new(math_alpha.outputs[0], mix_longest_distance.inputs[0])

    links.new(cr_distance.outputs[0], mix_longest_distance.inputs[1])
    links.new(cr_distance.outputs[1], bsdf.inputs[18])
    links.new(mix_longest_distance.outputs[0], hsv.inputs[4])
    if props.display.paint_style == mesh_manager.DISTANCE:
        links.new(vertex_colors_distance.outputs[0], sep_rgb.inputs[0])
    elif props.display.paint_style == mesh_manager.UNIFORM:
        links.new(rgb.outputs[0], mix_longest_distance.inputs[1])
    elif props.display.paint_style == mesh_manager.GROUP:
        links.new(vertex_colors_group.outputs[0], cr_distance.inputs[0])
    else:
        links.new(vertex_colors_neighbors.outputs[0], cr_distance.inputs[0])

    links.new(hsv.outputs[0], bsdf.inputs[0])
    links.new(bsdf.outputs[0], node_from_mat(mat, NodeNames.output).inputs[0])
