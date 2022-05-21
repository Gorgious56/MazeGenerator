import bpy
from mathutils import Vector
from maze_generator.blender.nodes.tool import create_node


def init_node_tree(tree):
    nodes = tree.nodes
    nodes.clear()
    input = create_node(nodes, bpy.types.NodeGroupInput)
    output = create_node(nodes, bpy.types.NodeGroupOutput)
    proxy = create_node(nodes, bpy.types.GeometryNodeJoinGeometry)

    output.location = input.location + Vector((200, 0))

    tree.inputs.clear()
    tree.outputs.clear()

    links = tree.links
    links.clear()
    links.new(proxy.outputs[0], output.inputs[0])
    links.new(input.outputs[0], output.inputs[0])

    nodes.remove(proxy)
