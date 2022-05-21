import bpy
from maze_generator.blender.geometry_nodes.factory.base import BaseGNTree


class ExtrudeEdgesUpwardGNTree(BaseGNTree):
    TREE_NAME = "MG_GN_EXTRUDE_EDGES_UPWARDS"

    def create_nodes(self):
        self.vector = self.create_node(bpy.types.FunctionNodeInputVector)
        self.vector.vector[2] = 1
        self.extrude = self.create_node(bpy.types.GeometryNodeExtrudeMesh)
        self.extrude.mode = "EDGES"

    def create_links(self):
        links = self.links
        links.new(self.input.outputs["Geometry"], self.extrude.inputs["Mesh"])
        links.new(self.input.outputs[-1], self.extrude.inputs["Offset Scale"])
        links.new(self.vector.outputs["Vector"], self.extrude.inputs["Offset"])
        links.new(self.extrude.outputs["Mesh"], self.output.inputs["Geometry"])
