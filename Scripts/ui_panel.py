import bpy


class MazeGeneratorPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_idname = "MG_Panel"
    bl_label = "Maze Generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MG'

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        mg_props = scene.mg_props

        # Create a simple row.
        layout.prop(mg_props, 'use_polar_grid')
        layout.prop(mg_props, 'maze_algorithm')
        layout.prop(mg_props, 'rows_or_radius')
        layout.prop(mg_props, 'seed')
        layout.label(text=" Walls:")
        row = layout.row()
        row.prop(mg_props, 'wall_height')
        row.prop(mg_props, 'wall_width')
        layout.label(text=" Simple Row:")

        row = layout.row()
        # row.prop(mg_props, "test_property")
        row.prop(scene, "frame_end")

        # Create an row where the buttons are aligned to each other.
        layout.label(text=" Aligned Row:")

        row = layout.row(align=True)
        row.prop(scene, "frame_start")
        row.prop(scene, "frame_end")

        # Create two columns, by using a split layout.
        split = layout.split()

        # First column
        col = split.column()
        col.label(text="Column One:")
        col.prop(scene, "frame_end")
        col.prop(scene, "frame_start")

        # Second column, aligned
        col = split.column(align=True)
        col.label(text="Column Two:")
        col.prop(scene, "frame_start")
        col.prop(scene, "frame_end")

        # Big render button
        layout.label(text="Big Button:")
        row = layout.row()
        row.scale_y = 3.0
        row.operator("maze.generate")

        # Different sizes in a row
        layout.label(text="Different button sizes:")
        row = layout.row(align=True)
        row.operator("maze.generate")

        # sub = row.row()
        # sub.scale_x = 2.0
        # sub.operator("object.simple_operator")

        # row.operator("object.simple_operator")
