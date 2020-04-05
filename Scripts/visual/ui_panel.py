import bpy
from .. maze_logic . algorithm_manager import is_algo_weaved, ALGORITHM_FROM_NAME, KruskalRandom, is_algo_incompatible
from . space_rep_manager import REP_REGULAR, REP_CYLINDER, REP_MEOBIUS, REP_TORUS, REP_BOX, REP_STAIRS
from . cell_type_manager import TRIANGLE, HEXAGON, POLAR, SQUARE
from .. utils . material_manager import MaterialManager
from .. visual . maze_visual import MazeVisual


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
        sub = row.row(align=True)
        sub.operator("maze.generate", icon='VIEW_ORTHO')
        sub.scale_x = 10.0

        sub = row.row(align=True)
        sub.prop(mg_props, 'auto_update', toggle=True, icon='FILE_REFRESH', text='')
        sub.prop(mg_props, 'auto_overwrite', toggle=True, icon='TRASH', text='')


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

        algo_incompatibility = is_algo_incompatible(mg_props)
        if algo_incompatibility:
            layout.label(text=algo_incompatibility, icon='ERROR')

        space_enum_icon = 'MESH_PLANE'
        if mg_props.maze_space_dimension == REP_REGULAR:
            space_enum_icon = 'MESH_CYLINDER'
        if mg_props.maze_space_dimension == REP_CYLINDER:
            space_enum_icon = 'GP_SELECT_STROKES'
        if mg_props.maze_space_dimension == REP_MEOBIUS:
            space_enum_icon = 'GP_SELECT_STROKES'
        if mg_props.maze_space_dimension == REP_TORUS:
            space_enum_icon = 'MESH_CUBE'
        if mg_props.maze_space_dimension == REP_STAIRS:
            space_enum_icon = 'NLA_PUSHDOWN'

        layout.prop_menu_enum(mg_props, 'maze_space_dimension', icon=space_enum_icon)

        if mg_props.cell_type == POLAR and mg_props.maze_space_dimension in (REP_CYLINDER, REP_MEOBIUS, REP_TORUS, REP_BOX):
            layout.label(text='Only Regular and Stairs for Polar cells', icon='ERROR')
        elif mg_props.cell_type == TRIANGLE or mg_props.cell_type == HEXAGON:
            if mg_props.maze_space_dimension in (REP_CYLINDER, REP_MEOBIUS, REP_TORUS):
                layout.label(text='Needs PAIR Columns (2, 4, 6, ...)', icon='ERROR')
            if mg_props.maze_space_dimension == REP_MEOBIUS and mg_props.maze_columns <= 5 * mg_props.maze_rows_or_radius:
                layout.label(text='Set Columns > 5 * Rows', icon='ERROR')
            elif mg_props.maze_space_dimension == REP_TORUS and mg_props.maze_columns > mg_props.maze_rows_or_radius:
                layout.label(text='Set Rows > Columns', icon='ERROR')
        elif mg_props.maze_space_dimension == REP_MEOBIUS and mg_props.maze_columns <= 3 * mg_props.maze_rows_or_radius:
            layout.label(text='Set Columns > 3 * Rows', icon='ERROR')
        elif mg_props.maze_space_dimension == REP_TORUS and 2 * mg_props.maze_columns > mg_props.maze_rows_or_radius:
            layout.label(text='Set Rows > 2 * Columns', icon='ERROR')
        elif mg_props.maze_space_dimension == REP_BOX:
            layout.label(text='Dimensions are 1 face of the cube', icon='QUESTION')
        row = layout.row(align=True)
        if mg_props.maze_space_dimension == REP_STAIRS:
            row.prop(mg_props, 'maze_stairs_scale', text='Scale')
        else:
            row.label()
        row.prop(mg_props, 'maze_stairs_weld', text='Weld')

        def maze_size_ui(prop_name, decrease, increase, text):
            row = layout.row(align=True)
            sub = row.row()
            sub.operator('maze.tweak_maze_size', text='', icon='REMOVE').tweak_size = decrease

            sub = row.row()
            sub.prop(mg_props, prop_name, slider=True, text=text)
            sub.scale_x = 10.0

            sub = row.row()
            sub.operator('maze.tweak_maze_size', text='', icon='ADD').tweak_size = increase
            return row

        maze_size_ui('maze_columns', [-1, 0, 0], [1, 0, 0], 'Columns').enabled = mg_props.cell_type != POLAR
        row = maze_size_ui('maze_rows_or_radius', [0, -1, 0], [0, 1, 0], 'Rows').enabled = True
        row = maze_size_ui('maze_levels', [0, 0, -1], [0, 0, 1], 'Levels').enabled = mg_props.maze_space_dimension == REP_REGULAR
        row = layout.row()
        row.prop(mg_props, 'seed')
        row.prop(mg_props, 'steps', icon='MOD_DYNAMICPAINT')

        layout.prop(mg_props, 'braid_dead_ends', slider=True, text='Open Dead Ends')
        layout.prop(mg_props, 'sparse_dead_ends')
        row = layout.row()
        row_2 = row.row()
        if mg_props.maze_algorithm == KruskalRandom.name:
            row_2.prop(mg_props, 'maze_weave', slider=True)
        else:
            row_2.prop(mg_props, 'maze_weave_toggle', toggle=True)
        row_2.enabled = is_algo_weaved(mg_props)

        box = layout.box()
        for setting in ALGORITHM_FROM_NAME[mg_props.maze_algorithm].settings:
            box.prop(mg_props, setting)


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
            cells = context.scene.objects['MG_Cells']
            self.layout.prop(cells, 'hide_viewport', text='')
            self.layout.prop(cells, 'hide_render', text='')
        except KeyError:
            pass

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        mg_props = scene.mg_props

        box = layout
        row = box.row(align=True)
        row.prop(mg_props, 'cell_inset', slider=True, text='Inset')
        row.prop(mg_props, 'cell_thickness', slider=True, text='Thickness')

        row = box.row(align=True)
        row.prop(mg_props, 'cell_contour', slider=True, text='Bevel')
        row.prop(mg_props, 'cell_contour_black', toggle=True, text='Black Outline')

        box.prop(mg_props, 'cell_wireframe', slider=True, text='Wireframe', icon='MOD_DECIM')

        row = box.row(align=True)
        row.prop(mg_props, 'cell_use_smooth', toggle=True, icon='SHADING_RENDERED', text='Shade Smooth')
        row.prop(mg_props, 'cell_subdiv', text='Subdivisions', icon='MOD_SUBSURF')

        box.prop(mg_props, 'cell_decimate', slider=True, text='Decimate', icon='MOD_DECIM')

        if mg_props.cell_subdiv > 0 and mg_props.cell_contour > 0:
            box.label(text='Bevel conflicts with Subdivision', icon='ERROR')
        if mg_props.cell_wireframe > 0 and mg_props.cell_contour > 0:
            box.label(text='Bevel can conflict with Wireframe', icon='QUESTION')


class WallsPanel(bpy.types.Panel):
    bl_idname = "MAZE_GENERATOR_PT_WallPanel"
    bl_label = " "
    bl_parent_id = 'MAZE_GENERATOR_PT_MainPanel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MG'
    # bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        self.layout.label(text='Walls', icon='SNAP_EDGE')
        try:
            wall = context.scene.objects['MG_Walls']
            self.layout.prop(wall, 'hide_viewport', text='')
            self.layout.prop(wall, 'hide_render', text='')
        except KeyError:
            pass

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mg_props = scene.mg_props

        row = layout.row(align=True)
        layout.prop(mg_props, 'wall_bevel', text='Bevel', slider=True)
        row.prop(mg_props, 'wall_height')
        row.prop(mg_props, 'wall_width', text='Thickness', slider=True)
        layout.prop(mg_props, 'wall_color', text='Color')
        layout.prop(mg_props, 'wall_hide', text='Auto-hide when insetting', toggle=True)


class DisplayPanel(bpy.types.Panel):
    bl_idname = "MAZE_GENERATOR_PT_DisplayPanel"
    bl_label = "Display"
    bl_parent_id = 'MAZE_GENERATOR_PT_MainPanel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MG'

    def draw_header(self, context):
        self.layout.label(text='', icon='BRUSH_DATA')

    def draw(self, context):
        layout = self.layout
        mg_props = context.scene.mg_props

        layout.prop(mg_props, 'paint_style')
        if mg_props.paint_style != 'DISTANCE':
            layout.prop(mg_props, 'seed_color_button', text='Randomize Colors', toggle=True)
        else:
            layout.prop(mg_props, 'show_only_longest_path', text='Show Longest Path')
            row = layout.row(align=True)
            if MazeVisual.Instance is None:
                row.operator("maze.generate", icon='VIEW_ORTHO', text='Update to tweak Colors')
            else:
                if MazeVisual.Mat_mgr and MazeVisual.Mat_mgr.cell_cr_distance_node:
                    layout.box().template_color_ramp(MazeVisual.Mat_mgr.cell_cr_distance_node, property="color_ramp", expand=True)
        layout.prop(mg_props, 'hue_shift', slider=True, text='Hue Shift', )
        layout.prop(mg_props, 'saturation_shift', slider=True, text='Saturation Shift')
        layout.prop(mg_props, 'value_shift', slider=True, text='Value Shift', icon='COLORSET_10_VEC')


class InfoPanel(bpy.types.Panel):
    bl_idname = "MAZE_GENERATOR_PT_InfoPanel"
    bl_label = "Info"
    bl_parent_id = 'MAZE_GENERATOR_PT_MainPanel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MG'
    # bl_options = {"DEFAULT_CLOSED"}

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
        layout.label(text='Disable Auto-overwrite (Trash icon) to keep modified values')
        layout.prop(mg_props, 'info_show_help', toggle=True)
