import bpy

from maze_generator.blender.collection.ui.preferences import draw as draw_collections
from maze_generator.blender.mesh.vertex_groups.ui.preferences import draw as draw_vertex_groups


class MazeGeneratorPreferences(bpy.types.AddonPreferences):
    bl_idname = "maze_generator"

    def draw(self, context):
        layout = self.layout

        mg_props = context.scene.mg_props

        draw_collections(layout, mg_props)
        draw_vertex_groups(layout, mg_props)
