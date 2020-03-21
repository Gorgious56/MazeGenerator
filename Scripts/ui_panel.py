import bpy


class MazeGeneratorPanel(bpy.types.Panel):
    bl_idname = "MAZE_GENERATOR_PT_MainPanel"
    bl_label = "Maze Generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MG'

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        mg_props = scene.mg_props

        # Create a simple row.
        layout.prop_menu_enum(mg_props, 'maze_algorithm')

        layout.prop(mg_props, 'rows_or_radius', slider=True)
        layout.prop(mg_props, 'seed')
        layout.prop(mg_props, 'braid_dead_ends', slider=True)
        layout.prop(mg_props, 'steps')

        box = layout.box()
        box.label(text="Walls")
        row = box.row()
        row.prop(mg_props, 'wall_height')
        row.prop(mg_props, 'wall_width')

        box = layout.box()
        box.label(text="Cells")
        box.prop_menu_enum(mg_props, 'cell_type')

        box = layout.box()
        box.label(text="Display")
        box.prop_menu_enum(mg_props, 'paint_style')
        row = box.row()
        row.prop(mg_props, 'seed_color_button', text='Randomize Colors', toggle=True)
        row.enabled = mg_props.paint_style != 'DISTANCE'
        box.prop(mg_props, 'hue_shift', slider=True, text='Hue Shift', )
        box.prop(mg_props, 'saturation_shift', slider=True, text='Saturation Shift')
        box.prop(mg_props, 'value_shift', slider=True, text='Value Shift')
        # box.prop(mg_props, 'color_shift')
        
        box = layout.box()
        box.label(text="Generation")
        box.prop(mg_props, 'auto_update', toggle=True)
        row = box.row()
        row.scale_y = 3.0
        row.operator("maze.generate")

        # row.prop(mg_props, 'paint_distance', toggle=True)

        # row = layout.row()
        # row.prop(mg_props, "test_property")
        # row.prop(scene, "frame_end")

        # Create an row where the buttons are aligned to each other.
        # layout.label(text=" Aligned Row:")

        # row = layout.row(align=True)
        # row.prop(scene, "frame_start")
        # row.prop(scene, "frame_end")

        # Create two columns, by using a split layout.
        # split = layout.split()

        # First column
        # col = split.column()
        # col.label(text="Column One:")
        # col.prop(scene, "frame_end")
        # col.prop(scene, "frame_start")

        # Second column, aligned
        # col = split.column(align=True)
        # col.label(text="Column Two:")
        # col.prop(scene, "frame_start")
        # col.prop(scene, "frame_end")

        # Big button

        # Different sizes in a row
        # layout.label(text="Different button sizes:")
        # row = layout.row(align=True)
        # row.operator("maze.generate")

        # sub = row.row()
        # sub.scale_x = 2.0
        # sub.operator("object.simple_operator")

        # row.operator("object.simple_operator")
