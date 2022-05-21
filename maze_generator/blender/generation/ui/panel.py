"""
Main Panel
"""


import bpy
from maze_generator.blender.generation.operators.generate_maze import MG_OT_maze_generate


class MazeGeneratorPanel(bpy.types.Panel):
    """
    Main Panel
    """

    bl_idname = "MAZE_GENERATOR_PT_MainPanel"
    bl_label = "Maze Generator"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MG"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        mg_props = scene.mg_props

        row = layout.row(align=True)
        row.scale_y = 2
        sub = row.row(align=True)
        sub.operator(MG_OT_maze_generate.bl_idname, icon="VIEW_ORTHO")
        sub.scale_x = 10.0

        sub = row.row(align=True)
        sub.prop(mg_props.generation, "auto_update", toggle=True, icon="FILE_REFRESH", text="")
        sub.prop(mg_props.generation, "auto_overwrite", toggle=True, icon="TRASH", text="")
        sub.prop(mg_props.interaction, "show_gizmos", toggle=True, icon="VIEW_PAN", text="")
