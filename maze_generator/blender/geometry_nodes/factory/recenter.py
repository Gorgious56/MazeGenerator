import bpy
from maze_generator.blender.geometry_nodes.factory.base import (
    BaseGNTree
)


class RecenterGNTree(BaseGNTree):
    TREE_NAME = "MG_GN_RECENTER"

    def create_nodes(self):
        self.bbox = self.create_node(bpy.types.GeometryNodeBoundBox)
        self.subtract = self.create_node(bpy.types.ShaderNodeVectorMath)
        self.subtract.operation = "SUBTRACT"
        self.scale = self.create_node(bpy.types.ShaderNodeVectorMath)
        self.scale.operation = "SCALE"
        self.scale.inputs["Scale"].default_value = 0.5
        self.set_position = self.create_node(bpy.types.GeometryNodeSetPosition)

    def create_links(self):
        links = self.links
        links.new(self.input.outputs["Geometry"], self.bbox.inputs["Geometry"])
        links.new(self.bbox.outputs["Min"], self.subtract.inputs[0])
        links.new(self.bbox.outputs["Max"], self.subtract.inputs[1])
        links.new(self.subtract.outputs["Vector"], self.scale.inputs["Vector"])
        links.new(self.input.outputs["Geometry"], self.set_position.inputs["Geometry"])
        links.new(self.scale.outputs["Vector"], self.set_position.inputs["Offset"])
        links.new(self.set_position.outputs["Geometry"], self.output.inputs["Geometry"])
