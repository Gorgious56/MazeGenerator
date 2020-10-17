"""
Path Panel
"""


import bpy


class PathPanel(bpy.types.Panel):
    """
    Path Panel
    """
    bl_idname = "MAZE_GENERATOR_PT_PathPanel"
    bl_label = "Path"
    bl_parent_id = 'MAZE_GENERATOR_PT_MainPanel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MG'
    order = 5

    @classmethod
    def poll(cls, context):
        objects = context.scene.mg_props.objects
        return objects.cells or objects.walls

    def draw_header(self, context):
        self.layout.label(text='', icon='OUTLINER_DATA_GREASEPENCIL')

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        mg_props = scene.mg_props

        layout.prop(mg_props, "maze_random_path")

        row = layout.row()
        row.prop(mg_props, "maze_outside_path")
        row.enabled = mg_props.maze_random_path

        row = layout.row()
        row.prop(mg_props, "maze_force_start", text="Start")
        row.enabled = not mg_props.maze_random_path

        row = layout.row()
        row.prop(mg_props, "maze_force_end", text="End")
        row.enabled = not mg_props.maze_random_path
