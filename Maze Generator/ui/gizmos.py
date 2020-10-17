"""
Module to handle add-on gizmos
"""
from math import radians
from mathutils import Matrix

from bpy.types import (
    GizmoGroup,
)


class MazeWidgetGroup(GizmoGroup):
    """
    Main Maze widget
    """
    bl_idname = "OBJECT_GGT_light_test"
    bl_label = "Test Light Widget"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT'}

    @classmethod
    def poll(cls, context):
        return context.scene.mg_props.objects.cells and context.scene.mg_props.show_gizmos

    def register_widget(self, widget, rotation):
        if not hasattr(self, "my_widgets"):
            setattr(self, "my_widgets", {})
        getattr(self, "my_widgets")[widget] = {'rotation': rotation}

    def setup_widget(self, props, prop_name, color=(1, 0, 0), rot_axis="X", rot_angle=0):
        new_widget = self.gizmos.new("GIZMO_GT_arrow_3d")
        # new_widget.offset = getattr(data, prop_name)
        new_widget.target_set_prop("offset", props, prop_name)
        new_widget.draw_style = 'BOX'

        new_widget.color = color
        new_widget.alpha = 1

        new_widget.color_highlight = color[0] + \
            0.4, color[1] + 0.4, color[2] + 0.4
        new_widget.alpha_highlight = 0.5
        self.register_widget(new_widget, Matrix.Rotation(
            radians(rot_angle), 4, rot_axis))

    def setup(self, context):
        mg_props = context.scene.mg_props
        self.setup_widget(mg_props, "maze_columns_gizmo",
                          color=(1, 0, 0), rot_axis='Y', rot_angle=90)
        self.setup_widget(mg_props, "maze_rows_or_radius_gizmo",
                          color=(0, 1, 0), rot_axis='X', rot_angle=-90)
        self.setup_widget(
            mg_props.objects.cells.modifiers[mg_props.mod_names.stairs], "strength", color=(0, 0, 1))
        # self.setup_widget(om.obj_cells.modifiers[mm.M_THICKNESS_DISP], "strength", color=(0, 0, 1), rot_axis='X', rot_angle=180)

    def refresh(self, context):
        if hasattr(self, "my_widgets"):
            widgets = getattr(self, "my_widgets")
            for widget, attributes in widgets.items():
                rotation = attributes['rotation']
                widget.matrix_basis = context.scene.mg_props.objects.cells.matrix_world.normalized() @ rotation
        # mpr = getattr(self, "column_widget")
