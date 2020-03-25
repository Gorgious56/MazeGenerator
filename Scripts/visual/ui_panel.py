import bpy
from .. maze_logic . algorithms . algorithm_manager import BIASED_ALGORITHMS
from . cell_type_manager import TRIANGLE, HEXAGON, POLAR, SQUARE


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

        row = layout.row(align=True)
        row.scale_y = 2
        sub = row.row()
        sub.operator("maze.generate", icon='VIEW_ORTHO')
        sub.scale_x = 10.0

        sub = row.row()
        sub.prop(mg_props, 'auto_update', toggle=True, icon='FILE_REFRESH', text='')

        # row.operator("object.simple_operator")


class WallsPanel(bpy.types.Panel):
    bl_idname = "MAZE_GENERATOR_PT_WallPanel"
    bl_label = " "
    bl_parent_id = 'MAZE_GENERATOR_PT_MainPanel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MG'
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        self.layout.label(text='Walls', icon='SNAP_EDGE')
        try:
            wall = context.scene.objects['Walls']
            self.layout.prop(wall, 'hide_viewport', text='')
            self.layout.prop(wall, 'hide_render', text='')
        except KeyError:
            pass

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mg_props = scene.mg_props

        row = layout.row(align=True)
        layout.prop(mg_props, 'wall_bevel', text='Wall Bevel', slider=True)
        row.prop(mg_props, 'wall_height')
        row.prop(mg_props, 'wall_width')
        layout.prop(mg_props, 'wall_color')
        layout.prop(mg_props, 'wall_hide', text='Auto-hide wall when insetting', toggle=True)


class CellsPanel(bpy.types.Panel):
    bl_idname = "MAZE_GENERATOR_PT_CellsPanel"
    bl_label = " "
    bl_parent_id = 'MAZE_GENERATOR_PT_MainPanel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MG'

    def draw_header(self, context):
        self.layout.label(text='Cells', icon='TEXTURE_DATA')
        try:
            cells = context.scene.objects['Cells']
            self.layout.prop(cells, 'hide_viewport', text='')
            self.layout.prop(cells, 'hide_render', text='')
        except KeyError:
            pass

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        mg_props = scene.mg_props

        box = layout.box()
        row = box.row()
        row.prop(mg_props, 'maze_weave', toggle=True)
        row.enabled = mg_props.cell_type == SQUARE
        row = box.row(align=True)
        row.prop(mg_props, 'cell_inset', slider=True, text='Inset')
        row.prop(mg_props, 'cell_contour', slider=True, text='Contour')
        box.prop(mg_props, 'cell_thickness', slider=True, text='Thickness')

        box = layout.box()
        box.prop(mg_props, 'paint_style')
        if mg_props.paint_style != 'DISTANCE':
            box.prop(mg_props, 'seed_color_button', text='Randomize Colors', toggle=True)
        else:
            box.prop(mg_props, 'show_only_longest_path', text='Show Longest Path')
            row = box.row(align=True)
            row.prop(mg_props, 'distance_color_start', text='Start')
            row.prop(mg_props, 'distance_color_end', text='End')
        box.prop(mg_props, 'hue_shift', slider=True, text='Hue Shift', )
        box.prop(mg_props, 'saturation_shift', slider=True, text='Saturation Shift')
        box.prop(mg_props, 'value_shift', slider=True, text='Value Shift', icon='COLORSET_10_VEC')


class ParametersPanel(bpy.types.Panel):
    bl_idname = "MAZE_GENERATOR_PT_ParametersPanel"
    bl_label = "Parameters"
    bl_parent_id = 'MAZE_GENERATOR_PT_MainPanel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MG'

    def draw_header(self, context):
        self.layout.label(text='', icon='PREFERENCES')

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        mg_props = scene.mg_props

        cell_enum_icon = 'MESH_PLANE'
        if mg_props.cell_type == POLAR:
            cell_enum_icon = 'MESH_CIRCLE'
        elif mg_props.cell_type == TRIANGLE:
            cell_enum_icon = 'OUTLINER_OB_MESH'
        elif mg_props.cell_type == HEXAGON:
            cell_enum_icon = 'SEQ_CHROMA_SCOPE'

        layout.prop_menu_enum(mg_props, 'cell_type', icon=cell_enum_icon)
        layout.prop(mg_props, 'maze_algorithm', icon='HAND', text='Solver')

        row = layout.row(align=True)
        sub = row.row()
        sub.operator('maze.tweak_row_number', text='', icon='REMOVE').add_or_remove = False

        sub = row.row()
        sub.prop(mg_props, 'rows_or_radius', slider=True, text='Size')
        sub.scale_x = 10.0

        sub = row.row()
        sub.operator('maze.tweak_row_number', text='', icon='ADD').add_or_remove = True

        row = layout.row()
        row.prop(mg_props, 'seed')
        row.prop(mg_props, 'steps', icon='MOD_DYNAMICPAINT')
        row = layout.row()
        row.prop(mg_props, 'maze_bias', slider=True, icon='FORCE_VORTEX')
        row.enabled = mg_props.maze_algorithm in BIASED_ALGORITHMS
        layout.prop(mg_props, 'braid_dead_ends', slider=True, text='Open Dead Ends')
        layout.prop(mg_props, 'sparse_dead_ends')


class InfoPanel(bpy.types.Panel):
    bl_idname = "MAZE_GENERATOR_PT_InfoPanel"
    bl_label = "Info"
    bl_parent_id = 'MAZE_GENERATOR_PT_MainPanel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MG'
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        self.layout.label(text='', icon='INFO')

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        mg_props = scene.mg_props
        gen_time = mg_props.generation_time
        if gen_time > 0:
            layout.label(text='Generation time : ' + str(gen_time) + ' ms', icon='TEMP')
        layout.label(text='Dead ends : ' + str(mg_props.dead_ends), icon='CON_FOLLOWPATH')
