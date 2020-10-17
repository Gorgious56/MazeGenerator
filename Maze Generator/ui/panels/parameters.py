"""
Parameters Panel
"""


import bpy
from ...maze_logic import cells as cell_mgr
from ...maze_logic.algorithms.manager import algorithm_class_from_name, KruskalRandom, is_algo_incompatible

class ParametersPanel(bpy.types.Panel):
    """
    Parameters Panel
    """
    bl_idname = "MAZE_GENERATOR_PT_ParametersPanel"
    bl_label = "Parameters"
    bl_parent_id = 'MAZE_GENERATOR_PT_MainPanel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MG'
    order = 1

    def draw_header(self, context):
        self.layout.label(text='', icon='PREFERENCES')

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        mg_props = scene.mg_props
        space_reps = mg_props.space_reps

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
            for setting in algorithm_class_from_name(mg_props.maze_algorithm).settings:
                if setting == 'maze_weave':
                    continue
                    if mg_props.maze_algorithm == KruskalRandom.name:
                        box.prop(mg_props, 'maze_weave', slider=True)
                    else:
                        box.prop(mg_props, 'maze_weave_toggle', toggle=True)
                else:
                    box.prop(mg_props, setting)
        if mg_props.cell_type == cell_mgr.POLAR and mg_props.maze_space_dimension in (space_reps.cylinder, space_reps.moebius, space_reps.torus, space_reps.moebius):
            layout.label(
                text='Only Regular and Stairs for Polar cells', icon='ERROR')
        elif mg_props.cell_type in (cell_mgr.TRIANGLE, cell_mgr.HEXAGON, cell_mgr.OCTOGON):
            if mg_props.maze_space_dimension in (space_reps.cylinder, space_reps.moebius, space_reps.torus):
                layout.label(
                    text='Needs PAIR Columns (2, 4, 6, ...)', icon='ERROR')
            if mg_props.maze_space_dimension == space_reps.moebius and mg_props.maze_columns <= 5 * mg_props.maze_rows_or_radius:
                layout.label(text='Set Columns > 5 * Rows', icon='ERROR')
            elif mg_props.maze_space_dimension == space_reps.torus and mg_props.maze_columns > mg_props.maze_rows_or_radius:
                layout.label(text='Set Rows > Columns', icon='ERROR')
        elif mg_props.maze_space_dimension == space_reps.moebius and mg_props.maze_columns <= 3 * mg_props.maze_rows_or_radius:
            layout.label(text='Set Columns > 3 * Rows', icon='ERROR')
        elif mg_props.maze_space_dimension == space_reps.torus and 2 * mg_props.maze_columns > mg_props.maze_rows_or_radius:
            layout.label(text='Set Rows > 2 * Columns', icon='ERROR')
        elif mg_props.maze_space_dimension == space_reps.moebius:
            layout.label(text='Dimensions are 1 face of the cube',
                         icon='QUESTION')

        def maze_size_ui(prop_name, decrease, increase, text):
            row = layout.row(align=True)
            sub = row.row()
            sub.operator('maze.tweak_maze_size', text='',
                         icon='REMOVE').tweak_size = decrease

            sub = row.row()
            sub.prop(mg_props, prop_name, slider=True, text=text)
            sub.scale_x = 10.0

            sub = row.row()
            sub.operator('maze.tweak_maze_size', text='',
                         icon='ADD').tweak_size = increase
            return row

        if mg_props.cell_type != cell_mgr.POLAR:
            maze_size_ui('maze_columns', [-1, 0, 0], [1, 0, 0], 'Columns')
        else:
            layout.prop(mg_props, 'maze_polar_branch', text='Branch amount')

        # row = layout.row()
        # row.prop(mg_props, "maze_columns")
        # row.active = False

        row = maze_size_ui('maze_rows_or_radius', [
            0, -1, 0], [0, 1, 0], 'Rows').enabled = True
        row = maze_size_ui('maze_levels', [
            0, 0, -1], [0, 0, 1], 'Levels').enabled = mg_props.maze_space_dimension == space_reps.regular and mg_props.cell_type == cell_mgr.SQUARE
        row = layout.row()
        row.prop(mg_props, 'seed')
        obj_cells = mg_props.objects.cells
        if obj_cells:
            try:
                cell_mask_mod = obj_cells.modifiers[mg_props.mod_names.mask]
                row.prop(cell_mask_mod, 'threshold', text='Steps')
            except (ReferenceError, KeyError):
                pass

        layout.prop(mg_props, 'keep_dead_ends', slider=True, text='Dead Ends')
        layout.prop(mg_props, 'sparse_dead_ends')

        box = layout.box()

        space_enum_icon = 'MESH_PLANE'
        if mg_props.maze_space_dimension == space_reps.regular:
            space_enum_icon = 'MESH_PLANE'
        if mg_props.maze_space_dimension == space_reps.cylinder:
            space_enum_icon = 'GP_SELECT_STROKES'
        if mg_props.maze_space_dimension == space_reps.moebius:
            space_enum_icon = 'GP_SELECT_STROKES'
        if mg_props.maze_space_dimension == space_reps.torus:
            space_enum_icon = 'MESH_CUBE'

        box.prop_menu_enum(mg_props, 'maze_space_dimension',
                           icon=space_enum_icon)

        if obj_cells:
            try:
                row = box.row(align=True)
                stairs_mod = obj_cells.modifiers.get(mg_props.mod_names.stairs)
                if stairs_mod:
                    row.prop(stairs_mod, 'strength', text='Stairs')

                row = box.row(align=True)
                tex_disp_mod = obj_cells.modifiers.get("MG_TEX_DISP")
                if tex_disp_mod:
                    row.prop(tex_disp_mod, 'strength', text='Inflate', slider=True)
                row.prop(mg_props.textures.displacement,
                        'noise_scale', text='Scale', slider=True)
            except ReferenceError:
                pass
