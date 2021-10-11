"""
Contains methods to access and modify the walls object material
"""


import bpy


def set_wall_material(props) -> None:
    obj_walls = props.objects.walls
    try:
        mat = obj_walls.material_slots[0].material
        if not props.core.auto_overwrite:
            return
    except IndexError:
        mat = bpy.data.materials.new("mat_walls")
        obj_walls.data.materials.append(mat)
        mat.use_nodes = True

    for node in mat.node_tree.nodes:
        if isinstance(node, bpy.types.ShaderNodeBsdfPrincipled):
            node.inputs[0].default_value = (0, 0, 0, 1)
            node.inputs['Roughness'].default_value = 1
            break
    props.display.materials.wall = mat
