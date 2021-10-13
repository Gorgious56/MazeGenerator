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
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MG"

    @classmethod
    def poll(cls, context):
        objects = context.scene.mg_props.objects
        return objects.cells or objects.walls

    def draw_header(self, context):
        self.layout.label(text="", icon="OUTLINER_DATA_GREASEPENCIL")

    def draw(self, context):
        layout = self.layout
        mg_props = context.scene.mg_props

        row = layout.row(align=True)
        row.prop(mg_props.display, "show_longest_path", text="Display Solution", toggle=True)
        obj_cells = mg_props.objects.cells
        if obj_cells:
            try:  # TODO get rid of try/except
                longest_path_mask_mod = obj_cells.modifiers.get(mg_props.mod_names.mask_longest_path)
                if longest_path_mask_mod:
                    row_2 = row.row()
                    row_2.prop(longest_path_mask_mod, "show_viewport", text="", icon="HIDE_OFF")
                    row_2.enabled = mg_props.display.show_longest_path
            except ReferenceError:
                pass

        scene = context.scene
        mg_props = scene.mg_props

        layout.props_enum(mg_props.path, "solution")
        row = layout.row()
        row.prop(mg_props.path, "force_outside", text="Force Outside Solution", toggle=1)
        row.enabled = mg_props.path.solution == "Random"

        row = layout.row()
        row.prop(mg_props.path, "start", text="Start")
        row.enabled = mg_props.path.solution == "Custom"

        row = layout.row()
        row.prop(mg_props.path, "end", text="End")
        row.enabled = mg_props.path.solution == "Custom"
