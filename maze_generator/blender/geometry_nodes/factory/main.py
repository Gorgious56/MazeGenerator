import bpy
from maze_generator.blender.nodes.tool import create_node, ensure_and_get_tree, get_input, get_output, plug_and_offset
from maze_generator.blender.geometry_nodes.factory.blank import init_node_tree
from maze_generator.blender.geometry_nodes.factory.recenter import get_or_create_recenter_node_group


def ensure_gn_modifier(obj, mod_name):
    if obj is None:
        return None

    mod = None
    for existing_mod in obj.modifiers:
        if existing_mod.type != "NODES":
            continue
        if existing_mod.name == mod_name or existing_mod.get("MG_FLAG"):
            mod = existing_mod
            break
    if mod is None:
        mod = obj.modifiers.new(type="NODES", name=mod_name)
    mod["MG_FLAG"] = 1
    ensure_gn_tree(existing_mod)
    return existing_mod


def ensure_gn_tree(mod):
    print("aa")
    if mod.type != "NODES":
        return
    tree = ensure_and_get_tree("MG_TREE", _type=bpy.types.GeometryNodeTree)
    print("aa")
    init_main_node_tree(tree)
    mod.node_group = tree
    return tree


def init_main_node_tree(tree):
    init_node_tree(tree)
    nodes = tree.nodes

    node_group = create_node(nodes, bpy.types.GeometryNodeGroup)
    node_group.node_tree = get_or_create_recenter_node_group()
    plug_and_offset(
        tree, get_input(nodes), "Geometry", node_group, "Geometry", "Geometry", get_output(nodes), "Geometry"
    )
    # for node in nodes:
    #     print(type(node))
