import bpy
from maze_generator.blender.nodes.tool import (
    ensure_and_get_tree,
    create_node,
    get_input,
    get_output,
    offset_nodes_chain,
)
from maze_generator.blender.geometry_nodes.factory.blank import init_node_tree


def get_or_create_extrude_edges_upward_node_group():
    tree = ensure_and_get_tree("MG_GN_EXTRUDE_EDGES_UPWARDS", _type=bpy.types.GeometryNodeTree)
    init_node_tree(tree)
    nodes = tree.nodes

    _input = get_input(nodes)
    output = get_output(nodes)
    vector = create_node(nodes, bpy.types.FunctionNodeInputVector)
    vector.vector[2] = 1
    extrude = create_node(nodes, bpy.types.GeometryNodeExtrudeMesh)
    extrude.mode = "EDGES"

    links = tree.links
    links.new(_input.outputs["Geometry"], extrude.inputs["Mesh"])
    links.new(_input.outputs[-1], extrude.inputs["Offset Scale"])
    _input.outputs["Offset Scale"].name = "Scale"
    links.new(vector.outputs["Vector"], extrude.inputs["Offset"])
    links.new(extrude.outputs["Mesh"], output.inputs["Geometry"])

    offset_nodes_chain(_input, vector, extrude, output)

    return tree
