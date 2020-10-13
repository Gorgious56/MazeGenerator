"""
Info Panel
"""

import bpy
from ..managers.grid_manager import GridManager


class InfoPanel(bpy.types.Panel):
    """
    Info Panel
    """
    bl_idname = "MAZE_GENERATOR_PT_InfoPanel"
    bl_label = "Info"
    bl_parent_id = 'MAZE_GENERATOR_PT_MainPanel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MG'
    order = 6
    # bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        objects = context.scene.mg_props.objects
        return objects.cells or objects.walls

    def draw_header(self, context):
        self.layout.label(text='', icon='INFO')

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        mg_props = scene.mg_props
        gen_time = mg_props.generation_time
        if gen_time > 0:
            layout.label(text='Generation time : ' +
                         str(gen_time) + ' ms', icon='TEMP')
        if GridManager.grid:
            layout.label(text='Dead ends : ' +
                         str(GridManager.grid.dead_ends_amount), icon='CON_FOLLOWPATH')
            layout.label(text='Max Neighbors : ' +
                         str(GridManager.grid.max_links_per_cell), icon='LIBRARY_DATA_DIRECT')
            layout.label(
                text='Groups : ' + str(len(GridManager.grid.groups)), icon='SELECT_SUBTRACT')
        # layout.label(text='Disable Auto-overwrite (Trash icon) to keep modified values')
            layout.operator('maze.sample')
