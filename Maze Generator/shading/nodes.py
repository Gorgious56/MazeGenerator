"""
This module handles creating, getting, setting node values and pointer properties
"""


from typing import Iterable
import bpy


def node_from_mat(mat, node_name):
    if mat is None or not mat.use_nodes:
        return None
    return mat.node_tree.nodes.get(node_name)


def create_node(
        nodes: bpy.types.Nodes,
        node_attr_name: str,
        _type: str,
        pos: Iterable[float] = None,
        inputs: dict = None,  # Index (integer or string), value
        outputs: dict = None,  # Index (integer or string), value
        attributes: dict = None) -> None:
    """
    Gets the node with the specified name from the nodes
    Or Creates it if it doesnt exist
    Then updates the inputs, outputs and attributes if necessary
    Then adds it to the MaterialManager for easy access
    """
    # node = nodes.get(node_attr_name)
    # if not node:
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

