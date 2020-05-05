import bpy
from ..managers import modifier_manager as mod_mgr
from ..managers.algorithm_manager import ALGORITHM_FROM_NAME, KruskalRandom, is_algo_incompatible
from ..managers import space_rep_manager as sp_rep
from ..managers import cell_type_manager as cell_mgr
from ..managers import texture_manager, material_manager
from ..managers.object_manager import ObjectManager
from ..managers.grid_manager import GridManager
from .maze_visual import MazeVisual


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
        if MazeVisual.scene:
            sub = row.row(align=True)
            sub.operator("maze.generate", icon='VIEW_ORTHO')
            sub.scale_x = 10.0

            sub = row.row(align=True)
            sub.prop(mg_props, 'auto_update', toggle=True, icon='FILE_REFRESH', text='')
            sub.prop(mg_props, 'auto_overwrite', toggle=True, icon='TRASH', text='')
        else:
            row.operator("maze.refresh", icon='FILE_REFRESH', text='Refresh')


class ParametersPanel(bpy.types.Panel):
    bl_idname = "MAZE_GENERATOR_PT_ParametersPanel"
    bl_label = "Parameters"
    bl_parent_id = 'MAZE_GENERATOR_PT_MainPanel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MG'

    @classmethod
    def poll(cls, context):
        return ObjectManager.obj_cells or ObjectManager.obj_walls

    def draw_header(self, context):
        self.layout.label(text='', icon='PREFERENCES')

    def draw(self, context):
        if not MazeVisual.scene:
            return
        layout = self.layout

        scene = context.scene
        mg_props = scene.mg_props

        cell_enum_icon = 'MESH_PLANE'
        if mg_props.cell_type == cell_mgr.POLAR:
            cell_enum_icon = 'MESH_CIRCLE'
        elif mg_props.cell_type == cell_mgr.TRIANGLE:
            cell_enum_icon = 'OUTLINER_OB_MESH'
        elif mg_props.cell_type == cell_mgr.HEXAGON:
            cell_enum_icon = 'SEQ_CHROMA_SCOPE'
        elif mg_props.cell_type == cell_mgr.OCTOGON:
            cell_enum_icon = 'MESH_ICOSPHERE'

        layout.prop_menu_enum(mg_props, 'cell_type', icon=cell_enum_icon)
        layout.prop(mg_props, 'maze_algorithm', icon='HAND', text='Solver')

        algo_incompatibility = is_algo_incompatible(mg_props)
        if algo_incompatibility:
            layout.label(text=algo_incompatibility, icon='ERROR')
        else:
            box = layout.box()
            for setting in ALGORITHM_FROM_NAME[mg_props.maze_algorithm].settings:
                if setting == 'maze_weave':
                    continue
                    if mg_props.maze_algorithm == KruskalRandom.name:
                        box.prop(mg_props, 'maze_weave', slider=True)
                    else:
                        box.prop(mg_props, 'maze_weave_toggle', toggle=True)
                else:
                    box.prop(mg_props, setting)

        if mg_props.cell_type == cell_mgr.POLAR and mg_props.maze_space_dimension in (sp_rep.REP_CYLINDER, sp_rep.REP_MEOBIUS, sp_rep.REP_TORUS, sp_rep.REP_BOX):
            layout.label(text='Only Regular and Stairs for Polar cells', icon='ERROR')
        elif mg_props.cell_type in (cell_mgr.TRIANGLE, cell_mgr.HEXAGON, cell_mgr.OCTOGON):
            if mg_props.maze_space_dimension in (sp_rep.REP_CYLINDER, sp_rep.REP_MEOBIUS, sp_rep.REP_TORUS):
                layout.label(text='Needs PAIR Columns (2, 4, 6, ...)', icon='ERROR')
            if mg_props.maze_space_dimension == sp_rep.REP_MEOBIUS and mg_props.maze_columns <= 5 * mg_props.maze_rows_or_radius:
                layout.label(text='Set Columns > 5 * Rows', icon='ERROR')
            elif mg_props.maze_space_dimension == sp_rep.REP_TORUS and mg_props.maze_columns > mg_props.maze_rows_or_radius:
                layout.label(text='Set Rows > Columns', icon='ERROR')
        elif mg_props.maze_space_dimension == sp_rep.REP_MEOBIUS and mg_props.maze_columns <= 3 * mg_props.maze_rows_or_radius:
            layout.label(text='Set Columns > 3 * Rows', icon='ERROR')
        elif mg_props.maze_space_dimension == sp_rep.REP_TORUS and 2 * mg_props.maze_columns > mg_props.maze_rows_or_radius:
            layout.label(text='Set Rows > 2 * Columns', icon='ERROR')
        elif mg_props.maze_space_dimension == sp_rep.REP_BOX:
            layout.label(text='Dimensions are 1 face of the cube', icon='QUESTION')

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

        maze_size_ui('maze_columns', [-1, 0, 0], [1, 0, 0], 'Columns').enabled = mg_props.cell_type != cell_mgr.POLAR
        row = maze_size_ui('maze_rows_or_radius', [0, -1, 0], [0, 1, 0], 'Rows').enabled = True
        row = maze_size_ui('maze_levels', [0, 0, -1], [0, 0, 1], 'Levels').enabled = mg_props.maze_space_dimension == sp_rep.REP_REGULAR and mg_props.cell_type == cell_mgr.SQUARE
        row = layout.row()
        row.prop(mg_props, 'seed')
        try:
            cell_mask_mod = ObjectManager.obj_cells.modifiers[mod_mgr.M_MASK]
        except (ReferenceError, KeyError):
            return
        row.prop(cell_mask_mod, 'threshold', text='Steps')

        layout.prop(mg_props, 'keep_dead_ends', slider=True, text='Dead Ends')
        layout.prop(mg_props, 'sparse_dead_ends')

        box = layout.box()

        space_enum_icon = 'MESH_PLANE'
        if mg_props.maze_space_dimension == sp_rep.REP_REGULAR:
            space_enum_icon = 'MESH_PLANE'
        if mg_props.maze_space_dimension == sp_rep.REP_CYLINDER:
            space_enum_icon = 'GP_SELECT_STROKES'
        if mg_props.maze_space_dimension == sp_rep.REP_MEOBIUS:
            space_enum_icon = 'GP_SELECT_STROKES'
        if mg_props.maze_space_dimension == sp_rep.REP_TORUS:
            space_enum_icon = 'MESH_CUBE'

        box.prop_menu_enum(mg_props, 'maze_space_dimension', icon=space_enum_icon)

        try:
            row = box.row(align=True)
            row.prop(ObjectManager.obj_cells.modifiers[mod_mgr.M_STAIRS], 'strength', text='Stairs')

            row = box.row(align=True)
            row.prop(ObjectManager.obj_cells.modifiers["MG_TEX_DISP"], 'strength', text='Inflate', slider=True)
            row.prop(texture_manager.TextureManager.tex_disp, 'noise_scale', text='Scale', slider=True)
        except ReferenceError:
            pass


class CellsPanel(bpy.types.Panel):
    bl_idname = "MAZE_GENERATOR_PT_CellsPanel"
    bl_label = " "
    bl_parent_id = 'MAZE_GENERATOR_PT_MainPanel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MG'

    @classmethod
    def poll(cls, context):
        return ObjectManager.obj_cells

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

        box = layout.box()

        try:
            cell_thickness_mod = ObjectManager.obj_cells.modifiers[mod_mgr.M_THICKNESS_DISP]
            cell_wire_mod = ObjectManager.obj_cells.modifiers[mod_mgr.M_WIREFRAME]
            cell_bevel_mod = ObjectManager.obj_cells.modifiers[mod_mgr.M_BEVEL]
            cell_subdiv_mod = ObjectManager.obj_cells.modifiers[mod_mgr.M_SUBDIV]
            cell_stairs = ObjectManager.obj_cells.modifiers[mod_mgr.M_STAIRS]
        except (ReferenceError, KeyError):
            return

        box.prop(mg_props, 'cell_inset', slider=True, text='Inset')
        row = box.row(align=True)
        row.prop(cell_thickness_mod, 'strength', text='Thickness')
        if cell_stairs.strength != 0:
            row.prop(mg_props, 'maze_basement', text='Basement', toggle=True)
        row = box.row(align=True)
        row.prop(cell_subdiv_mod, 'levels', text='Subdiv')
        row.prop(mg_props, 'cell_decimate', slider=True, text='Decimate', icon='MOD_DECIM')

        box.prop(mg_props, 'cell_use_smooth', toggle=True, icon='SHADING_RENDERED', text='Shade Smooth')

        if cell_subdiv_mod.levels > 0 and (cell_bevel_mod.width > 0 or cell_wire_mod.thickness > 0):
            box.label(text='Bevel conflicts with Subdivision', icon='ERROR')

        box = layout.box()
        box.label(text='Contour')

        row = box.row(align=True)

        bevel_row = row.row()
        bevel_row.prop(cell_bevel_mod, 'width', text='Bevel')
        bevel_row.enabled = cell_wire_mod.thickness == 0

        wireframe_row = row.row()
        wireframe_row.prop(cell_wire_mod, 'thickness', slider=True, text='Wireframe')
        wireframe_row.enabled = ObjectManager.obj_cells.modifiers[mod_mgr.M_BEVEL].width == 0

        row = box.row(align=True)
        row.prop(mg_props, 'cell_contour_black', toggle=True, text='Black Outline')

        replace_row = row.row()
        replace_row.prop(cell_wire_mod, 'use_replace', toggle=True)
        replace_row.enabled = cell_wire_mod.thickness > 0

        if (cell_wire_mod.thickness > 0 or cell_bevel_mod.width > 0) and mg_props.cell_inset < 0.1:
            box.label(text='Set Inset > 0,1', icon='ERROR')
        if cell_bevel_mod.width > 0 and (cell_thickness_mod.strength == 0 and not mg_props.maze_basement):
            box.label(text='Set Cell Thickness != 0 or Toggle Basement', icon='ERROR')


class WallsPanel(bpy.types.Panel):
    bl_idname = "MAZE_GENERATOR_PT_WallPanel"
    bl_label = " "
    bl_parent_id = 'MAZE_GENERATOR_PT_MainPanel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MG'
    # bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return ObjectManager.obj_walls

    def draw_header(self, context):
        self.layout.label(text='Walls', icon='SNAP_EDGE')
        wall_hide = context.scene.mg_props.wall_hide
        self.layout.prop(context.scene.mg_props, 'wall_hide', text='', icon='HIDE_ON' if wall_hide else 'HIDE_OFF')

    def draw(self, context):
        if not MazeVisual.scene:
            return
        layout = self.layout

        try:
            wall_solid_mod = ObjectManager.obj_walls.modifiers[mod_mgr.M_SOLID]
            wall_screw_mod = ObjectManager.obj_walls.modifiers[mod_mgr.M_SCREW]
            wall_bevel_mod = ObjectManager.obj_walls.modifiers[mod_mgr.M_BEVEL]
            wall_bsdf_node = material_manager.MaterialManager.wall_principled
        except ReferenceError:
            return
        row = layout.row(align=True)
        layout.prop(wall_bevel_mod, 'width', text='Bevel')
        row.prop(wall_screw_mod, 'screw_offset', text='Height')
        row.prop(wall_solid_mod, 'thickness')
        layout.prop(wall_bsdf_node.inputs[0], 'default_value', text='Color')


class DisplayPanel(bpy.types.Panel):
    bl_idname = "MAZE_GENERATOR_PT_DisplayPanel"
    bl_label = "Display"
    bl_parent_id = 'MAZE_GENERATOR_PT_MainPanel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MG'

    @classmethod
    def poll(cls, context):
        return ObjectManager.obj_cells or ObjectManager.obj_walls

    def draw_header(self, context):
        self.layout.label(text='', icon='BRUSH_DATA')

    def draw(self, context):
        if not MazeVisual.scene:
            return
        layout = self.layout
        mg_props = context.scene.mg_props

        box = layout.box()
        box.prop(mg_props, 'paint_style')
        row = box.row(align=True)
        row.prop(mg_props, 'show_longest_path', text='Longest Path', toggle=True)
        try:
            longest_path_mask_mod = ObjectManager.obj_cells.modifiers[mod_mgr.M_MASK_LONGEST_PATH]
            row_2 = row.row()
            row_2.prop(longest_path_mask_mod, 'show_viewport', text='Hide Rest', toggle=True)
            row_2.enabled = mg_props.show_longest_path
        except ReferenceError:
            pass
        if mg_props.paint_style == 'UNIFORM':
            box.prop(material_manager.MaterialManager.cell_rgb_node.outputs[0], 'default_value', text='Color')
        else:
            row = box.row(align=True)
            row.box().template_color_ramp(material_manager.MaterialManager.cell_cr_distance_node, property="color_ramp", expand=True)

        box.prop(material_manager.MaterialManager.cell_hsv_node.inputs[0], 'default_value', text='Hue Shift', slider=True)
        box.prop(material_manager.MaterialManager.cell_hsv_node.inputs[1], 'default_value', text='Saturation Shift', slider=True)
        box.prop(material_manager.MaterialManager.cell_hsv_node.inputs[2], 'default_value', text='Value Shift', slider=True)


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
        if GridManager.grid:
            layout.label(text='Dead ends : ' + str(GridManager.grid.dead_ends_amount), icon='CON_FOLLOWPATH')
            layout.label(text='Max Neighbors : ' + str(GridManager.grid.max_links_per_cell), icon='LIBRARY_DATA_DIRECT')
            layout.label(text='Groups : ' + str(len(GridManager.grid.groups)), icon='SELECT_SUBTRACT')
        # layout.label(text='Disable Auto-overwrite (Trash icon) to keep modified values')
            layout.operator('maze.sample')
