import bpy
from mathutils import Vector
from maze_generator.blender.geometry_nodes.factory.extrude_edges_upwards import ExtrudeEdgesUpwardGNTree
from maze_generator.blender.nodes.tool import (
    create_node,
    ensure_and_get_tree,
    get_input,
    get_output,
    plug_and_offset_geometry_sockets,
)
from maze_generator.blender.geometry_nodes.factory.blank import init_node_tree
from maze_generator.blender.geometry_nodes.factory.recenter import RecenterGNTree


def ensure_gn_modifier(obj, mod_name):
    if obj is None:
        return None

    mod = None
    for existing_mod in obj.modifiers:
        if existing_mod.type != "NODES":
            continue
        if existing_mod.name == mod_name or existing_mod.get(mod_name):
            mod = existing_mod
            break
    if mod is None:
        mod = obj.modifiers.new(type="NODES", name=mod_name)
    mod[mod_name] = 1
    return mod


def ensure_gn_tree(mod):
    if mod.type != "NODES":
        return
    tree = ensure_and_get_tree("MG_TREE", _type=bpy.types.GeometryNodeTree)
    init_main_node_tree(tree)
    mod.node_group = tree
    return tree


def init_main_node_tree(tree):
    nodes = tree.nodes
    # for node in nodes:
    #     print(type(node))
    init_node_tree(tree)

    _input = get_input(nodes)
    output = get_output(nodes)

    recenter = create_node(nodes, bpy.types.GeometryNodeGroup)
    recenter.node_tree = RecenterGNTree().get()
    plug_and_offset_geometry_sockets(tree, _input, recenter, output)

    merge_by_distance = create_node(nodes, bpy.types.GeometryNodeMergeByDistance)
    plug_and_offset_geometry_sockets(tree, _input, merge_by_distance, recenter)

    extrude_edges_upward = create_node(nodes, bpy.types.GeometryNodeGroup)
    extrude_edges_upward.node_tree = ExtrudeEdgesUpwardGNTree().get()
    plug_and_offset_geometry_sockets(tree, recenter, extrude_edges_upward, output)

    links = tree.links
    links.new(_input.outputs[-1], extrude_edges_upward.inputs[1])

    _input.location -= Vector((0, 200))
