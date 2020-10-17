"""
Main Panel
"""


import bpy
from .parameters import ParametersPanel
from .cells import CellsPanel
from .walls import WallsPanel
from .display import DisplayPanel
from .path import PathPanel
from .info import InfoPanel


class MazeGeneratorPanel(bpy.types.Panel):
    """
    Main Panel
    """
    bl_idname = "MAZE_GENERATOR_PT_MainPanel"
    bl_label = "Maze Generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MG'
    order = 0
    child_panels_ordered = sorted(
        [
            ParametersPanel,
            CellsPanel,
            WallsPanel,
            DisplayPanel,
            PathPanel,
            InfoPanel
        ],
        key=lambda panel: panel.order)

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        mg_props = scene.mg_props

        row = layout.row(align=True)
        row.scale_y = 2
        sub = row.row(align=True)
        sub.operator("maze.generate", icon='VIEW_ORTHO')
        sub.scale_x = 10.0

        sub = row.row(align=True)
        sub.prop(mg_props, 'auto_update', toggle=True,
                 icon='FILE_REFRESH', text='')
        sub.prop(mg_props, 'auto_overwrite',
                 toggle=True, icon='TRASH', text='')
        sub.prop(mg_props, 'show_gizmos', toggle=True,
                 icon='VIEW_PAN', text='')
        # else:
        #     row.operator("maze.refresh", icon='FILE_REFRESH', text='Refresh')

    def register():
        for panel_class in MazeGeneratorPanel.child_panels_ordered:
            bpy.utils.register_class(panel_class)            
