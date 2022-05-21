import bpy
from maze_generator.blender.nodes.tool import (
    ensure_and_get_tree,
    create_node,
    get_input,
    get_output,
    offset_nodes_chain,
)
from maze_generator.blender.geometry_nodes.factory.blank import init_node_tree


class BaseGNTree:
    TREE_NAME = "MG_GN_RECENTER"

    def __init__(self) -> None:
        self.tree = ensure_and_get_tree(self.TREE_NAME, _type=bpy.types.GeometryNodeTree)
        init_node_tree(self.tree)
        self.nodes = self.tree.nodes
        self.links = self.tree.links
        self.input = get_input(self.nodes)
        self.output = get_output(self.nodes)
        self.nodes_chain = [self.input]
        self.create_nodes()
        self.nodes_chain.append(self.output)
        offset_nodes_chain(*self.nodes_chain)
        self.create_links()

    def get(self):
        return self.tree

    def create_node(self, _type):
        new_node = create_node(self.nodes, _type)
        self.nodes_chain.append(new_node)
        return new_node

    def create_nodes(self):
        pass

    def create_links(self):
        pass
