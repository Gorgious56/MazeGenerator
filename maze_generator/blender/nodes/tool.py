import bpy
from mathutils import Vector


def get_tree_with_flag(flag):
    return next((t for t in bpy.data.node_groups if t.get(flag)), None)


def traverse_tree_right(node):
    yield node
    for output in node.outputs:
        if output.is_linked():
            for link in output.links:
                to_socket = link.to_socket
                yield from traverse_tree_right(to_socket.node)


def plug_and_offset(tree, from_node, from_socket, new_node, new_input_socket, new_output_socket, to_node, to_socket):
    links = tree.links
    links.new(from_node.outputs[from_socket], new_node.inputs[new_input_socket])
    links.new(new_node.outputs[new_output_socket], to_node.inputs[to_socket])

    offset_nodes(from_node, new_node)
    nodes_to_offset = [new_node] + list(set(traverse_tree_right(to_node)))
    offset_nodes_chain(*nodes_to_offset)


def get_input(nodes):
    return next(n for n in nodes if isinstance(n, bpy.types.NodeGroupInput))


def get_output(nodes):
    return next(n for n in nodes if isinstance(n, bpy.types.NodeGroupOutput))


def create_node(nodes, _type):
    return nodes.new(_type.__name__)


def ensure_and_get_tree(name, _type):
    tree = get_tree_with_flag(name)
    if tree is None:
        tree = bpy.data.node_groups.new(name=name, type=_type.__name__)
        tree[name] = True
    return tree


def offset_nodes_chain(*nodes, offset=(200, 0)):
    if len(nodes) < 2:
        return
    for i in range(len(nodes) - 1):
        offset_nodes(nodes[i], nodes[i + 1], offset)


def offset_nodes(from_node, to_node, offset=(200, 0)):
    to_node.location = from_node.location + Vector(offset)
