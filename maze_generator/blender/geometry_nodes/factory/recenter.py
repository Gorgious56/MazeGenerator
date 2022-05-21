import bpy
from maze_generator.blender.nodes.tool import (
    ensure_and_get_tree,
    create_node,
    get_input,
    get_output,
    offset_nodes_chain,
)
from maze_generator.blender.geometry_nodes.factory.blank import init_node_tree


def get_or_create_recenter_node_group():
    tree = ensure_and_get_tree("MG_GN_RECENTER", _type=bpy.types.GeometryNodeTree)
    init_node_tree(tree)

    nodes = tree.nodes
    bbox = create_node(nodes, bpy.types.GeometryNodeBoundBox)
    subtract = create_node(nodes, bpy.types.ShaderNodeVectorMath)
    subtract.operation = "SUBTRACT"
    scale = create_node(nodes, bpy.types.ShaderNodeVectorMath)
    scale.operation = "SCALE"
    scale.inputs["Scale"].default_value = 0.5
    set_position = create_node(nodes, bpy.types.GeometryNodeSetPosition)
    input = get_input(nodes)
    output = get_output(nodes)

    offset_nodes_chain(input, bbox, subtract, scale, set_position, output)

    links = tree.links
    links.new(input.outputs["Geometry"], bbox.inputs["Geometry"])
    links.new(bbox.outputs["Min"], subtract.inputs[0])
    links.new(bbox.outputs["Max"], subtract.inputs[1])
    links.new(subtract.outputs["Vector"], scale.inputs["Vector"])
    links.new(input.outputs["Geometry"], set_position.inputs["Geometry"])
    links.new(scale.outputs["Vector"], set_position.inputs["Offset"])
    links.new(set_position.outputs["Geometry"], output.inputs["Geometry"])

    return tree
