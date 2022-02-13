import bpy
from mathutils import Vector
from numpy import vectorize


class MazeObject:
    def __init__(self, mesh, collection) -> None:
        self.obj = bpy.data.objects.new("Maze", object_data=mesh)
        collection.objects.link(self.obj)
        self.ensure_gn()

    def _create_gn(self, name):
        self.mod = self.obj.modifiers.new(name, type="NODES")
        tree = self.mod.node_group
        input_node = next(n for n in tree.nodes if isinstance(n, bpy.types.NodeGroupInput))
        output_node = next(n for n in tree.nodes if isinstance(n, bpy.types.NodeGroupOutput))

        cube_node = tree.nodes.new(type="GeometryNodeMeshCube")
        cube_node.inputs[0].default_value = (0.1, 1, 1)
        cube_node.location = input_node.location - Vector((0, 120))

        instance_node = tree.nodes.new(type="GeometryNodeInstanceOnPoints")
        instance_node.location = input_node.location + Vector((200, 0))

        tree.links.new(input_node.outputs[0], instance_node.inputs[0])
        tree.links.new(input_node.outputs[1], instance_node.inputs[5])
        tree.links.new(cube_node.outputs[0], instance_node.inputs[2])
        tree.links.new(instance_node.outputs[0], output_node.inputs[0])

        rotation_input_name = tree.inputs[1].identifier
        bpy.ops.object.geometry_nodes_input_attribute_toggle(
            {"object": self.obj}, prop_path=f'["{rotation_input_name}_use_attribute"]', modifier_name="MG_Walls"
        )
        self.mod[f"{rotation_input_name}_attribute_name"] = "rotation"

    def ensure_gn(self):
        gn_name = "MG_Walls"
        self.mod = self.obj.modifiers.get(gn_name)
        if self.mod is None:
            self._create_gn(gn_name)
