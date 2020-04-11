
import math
from Scripts.visual.space_rep_manager import REP_REGULAR, REP_CYLINDER, REP_MEOBIUS, REP_TORUS, REP_BOX, REP_STAIRS
from Scripts.visual.cell_visual import DISTANCE, GROUP, NEIGHBORS, DISPLACE, STAIRS, UNIFORM
from Scripts.visual.cell_type_manager import POLAR, SQUARE, TRIANGLE, HEXAGON

WALL_WELD_NAME = 'MG_WELD'
WALL_SCREW_NAME = 'MG_SCREW'
WALL_SOLIDIFY_NAME = 'MG_SOLIDIFY'
WALL_BEVEL_NAME = 'MG_BEVEL'

CELL_WELD_NAME = 'MG_WELD'
CELL_WELD_2_NAME = 'MG_WELD_2'
CELL_SOLIDIFY_NAME = 'MG_SOLIDIFY'
CELL_DECIMATE_NAME = 'MG_DECIMATE'
CELL_DECIMATE_PLANAR_NAME = 'MG_DECIMATE_PLANAR'
CELL_SUBSURF_NAME = 'MG_SUBSURF'
CELL_BEVEL_NAME = 'MG_CONTOUR'
CELL_WIREFRAME_NAME = 'MG_WIREFRAME'
CELL_DISPLACE_NAME = 'MG_DISPLACE'
CELL_CYLINDER_NAME = 'MG_CYLINDER'
CELL_WELD_CYLINDER_NAME = 'MG_CYLINDER_WELD'
CELL_MOEBIUS_NAME = 'MG_MOEBIUS'
CELL_TORUS_NAME = 'MG_TORUS'
CELL_STAIRS_NAME = 'MG_STAIRS'
CELL_TEX_DISP = 'MG_TEX_DISP'

VISIBILIY = 'VISIBILITY'


def generate_drivers(MV, force=False):
    if force:
        def add_mod_driver(obj_from, obj_to, prop_from, prop_to, mod_name, expression):
            if prop_to == VISIBILIY:
                add_driver_to(obj_to.modifiers[mod_name], 'show_render', 'var', 'OBJECT', obj_from, 'modifiers["' + mod_name + '"].' + prop_from, expression)
                add_driver_to(obj_to.modifiers[mod_name], 'show_viewport', 'var', 'OBJECT', obj_from, 'modifiers["' + mod_name + '"].' + prop_from, expression)
            else:
                add_driver_to(obj_to.modifiers[mod_name], prop_to, 'var', 'OBJECT', obj_from, 'modifiers["' + mod_name + '"].' + prop_from, expression)

        for drv in (
            (MV.obj_walls, 'strength', 'strength', CELL_TEX_DISP, 'var'),
            (MV.obj_walls, 'strength', VISIBILIY, CELL_TEX_DISP, 'var != 0'),
            (MV.obj_walls, 'strength', 'strength', CELL_STAIRS_NAME, 'var'),
            (MV.obj_walls, 'strength', VISIBILIY, CELL_STAIRS_NAME, 'var != 0'),
            (MV.obj_walls, 'merge_threshold', 'merge_threshold', WALL_WELD_NAME, 'var'),

            (MV.obj_cells, 'strength', 'show_render', CELL_TEX_DISP, 'var != 0'),
            (MV.obj_cells, 'strength', VISIBILIY, CELL_TEX_DISP, 'var != 0'),
            (MV.obj_cells, 'strength', VISIBILIY, CELL_STAIRS_NAME, 'var != 0'),
            (MV.obj_cells, 'thickness', VISIBILIY, CELL_WIREFRAME_NAME, 'var != 0'),
            (MV.obj_cells, 'width', VISIBILIY, CELL_BEVEL_NAME, 'var != 0'),
            (MV.obj_cells, 'levels', VISIBILIY, CELL_SUBSURF_NAME, 'var > 0'),
            (MV.obj_cells, 'levels', 'render_levels', CELL_SUBSURF_NAME, 'var'),
        ):
            add_mod_driver(MV.obj_cells, drv[0], drv[1], drv[2], drv[3], drv[4])

        # We need 2 variables for this driver :
        for prop in ('show_viewport', 'show_render'):
            add_driver_to_vars(
                MV.obj_cells.modifiers[CELL_DECIMATE_PLANAR_NAME],
                prop,
                (
                    ('subdiv', 'OBJECT', MV.obj_cells, 'modifiers["' + CELL_SUBSURF_NAME + '"].levels'),
                    ('cell_inset', 'SCENE', MV.scene, 'mg_props.cell_inset'),
                ),
                expression='subdiv == 0 and cell_inset > 0'
            )

        # Scale the cylinder and torus objects when scaling the size of the maze
        for i, obj in enumerate((MV.obj_cylinder, MV.obj_torus)):
            drvList = obj.driver_add('scale')
            for fc in drvList:
                drv = fc.driver
                try:
                    var = drv.variables[0]
                except IndexError:
                    var = drv.variables.new()

                var.name = 'var'
                var.type = 'SINGLE_PROP'

                target = var.targets[0]
                target.id_type = 'SCENE'
                target.id = MV.scene
                target.data_path = 'mg_props.maze_columns' if i == 0 else 'mg_props.maze_rows_or_radius'

                exp = 'var * 0.314'
                if MV.props.cell_type == SQUARE:
                    exp = 'var * 0.15915'
                elif MV.props.cell_type == TRIANGLE:
                    if i == 0:
                        exp = 'var * 0.07963'
                    else:
                        exp = 'var * 0.13791'
                elif MV.props.cell_type == HEXAGON:
                    if i == 0:
                        exp = 'var * 0.2388'
                    else:
                        exp = 'var * 0.2758'

                drv.expression = exp


def setup_modifiers_and_drivers(MV):
    ow = MV.props.auto_overwrite
    mod_dic = {
        MV.obj_walls: (
            ('DISPLACE', CELL_STAIRS_NAME, {
                'direction': 'Z',
                'vertex_group': STAIRS,
                'mid_level': 0,
                'strength': 0,
            }),
            ('DISPLACE', CELL_TEX_DISP, {
                'texture': MV.tex_disp,
                'direction': 'Z',
                'strength': 0,
            }),
            ('WELD', WALL_WELD_NAME, {}),
            ('SCREW', WALL_SCREW_NAME, {
                'angle': 0,
                'steps': 1,
                'render_steps': 1,
                'screw_offset': ('wall_height', None),
                'use_smooth_shade': ('wall_bevel', 'var > 0.005'),
            }),
            ('SOLIDIFY', WALL_SOLIDIFY_NAME, {
                'show_viewport': ('wall_width', 'var != 0'),
                'show_render': ('wall_width', 'var != 0'),
                'solidify_mode': 'NON_MANIFOLD',
                'thickness': ('wall_width', None),
                'offset': 0,
            }),
            ('BEVEL', WALL_BEVEL_NAME, {
                'show_viewport': ('wall_bevel', 'var != 0'),
                'show_render': ('wall_bevel', 'var != 0'),
                'segments': 4,
                'limit_method': 'ANGLE',
                'use_clamp_overlap': False,
                'width': ('wall_bevel', None),
            }),
            ('DISPLACE', CELL_DISPLACE_NAME, {
                'show_viewport': ('maze_space_dimension', 'int(var) == ' + REP_CYLINDER + ' or int(var) == ' + REP_MEOBIUS),
                'show_render': ('maze_space_dimension', 'int(var) == ' + REP_CYLINDER + ' or int(var) == ' + REP_MEOBIUS),
                'strength': ('wall_height', '-var'),
                'direction': 'Z',
                'mid_level': 0.5,
            }),
            ('SIMPLE_DEFORM', CELL_MOEBIUS_NAME, {
                'show_viewport': ('maze_space_dimension', 'int(var) == ' + REP_MEOBIUS),
                'show_render': ('maze_space_dimension', 'int(var) == ' + REP_MEOBIUS),
                'angle': 2 * math.pi + (1 / 16 if MV.props.cell_type == TRIANGLE else 0),
            }),
            ('CURVE', CELL_CYLINDER_NAME, {
                'show_viewport': ('maze_space_dimension', f'int(var) in ({REP_CYLINDER}, {REP_MEOBIUS}, {REP_TORUS})'),
                'show_render': ('maze_space_dimension', f'int(var) in ({REP_CYLINDER}, {REP_MEOBIUS}, {REP_TORUS})'),
                'object': MV.obj_cylinder,
            }),
            ('CURVE', CELL_TORUS_NAME, {
                'show_viewport': ('maze_space_dimension', 'int(var) == ' + REP_TORUS),
                'show_render': ('maze_space_dimension', 'int(var) == ' + REP_TORUS),
                'object': MV.obj_torus,
                'deform_axis': 'POS_Y',
            }),
            ('WELD', CELL_WELD_CYLINDER_NAME, {
                'show_viewport': ('maze_space_dimension', REP_BOX + " > int(var) > " + REP_STAIRS),
                'show_render': ('maze_space_dimension', REP_BOX + " > int(var) > " + REP_STAIRS),
                'merge_threshold': 0.1,
            }),
        ),
        MV.obj_cells: (
            ('DISPLACE', CELL_STAIRS_NAME, {
                'direction': 'Z',
                'vertex_group': STAIRS,
                'mid_level': 0, 'strength': 0,
            }),
            ('WELD', CELL_WELD_NAME, {
                'vertex_group': DISPLACE,
                'invert_vertex_group': True,
                'merge_threshold': 0.04,
            }),
            ('WELD', CELL_WELD_2_NAME, {
                'show_viewport': ('maze_weave', 'var != 0'),
                'show_render': ('maze_weave', 'var != 0'),
                'vertex_group': DISPLACE,
                'invert_vertex_group': False,
            }),
            ('DISPLACE', CELL_TEX_DISP, {
                'texture': MV.tex_disp,
                'direction': 'Z',
                'strength': 0,
            }),
            ('SOLIDIFY', CELL_SOLIDIFY_NAME, {
                'show_viewport': ('cell_thickness', 'var != 0'),
                'show_render': ('cell_thickness', 'var != 0'),
                'offset': ('maze_space_dimension', '-1 if int(var) == ' + REP_REGULAR + ' or int(var) == ' + REP_STAIRS + ' else 0'),
                'thickness': ('cell_thickness', None),
                'thickness_vertex_group': ('cell_thickness', 'max(0, 1 - abs(var / 2))'),
                'use_even_offset': True,
                'vertex_group': DISPLACE,
                'invert_vertex_group': True,
            }),
            ('DISPLACE', CELL_DISPLACE_NAME, {
                'show_viewport': ('cell_thickness', 'var != 0'),
                'show_render': ('cell_thickness', 'var != 0'),
                'strength': ('cell_thickness', '- (var + (abs(var) / var * 0.1)) if var != 0 else 0'),
                'direction': 'Z',
                'vertex_group': DISPLACE,
                'mid_level': 0,
            }),
            ('SIMPLE_DEFORM', CELL_MOEBIUS_NAME, {
                'show_viewport': ('maze_space_dimension', "int(var) == " + REP_MEOBIUS),
                'show_render': ('maze_space_dimension', "int(var) == " + REP_MEOBIUS),
                'angle': 2 * math.pi + (1 / 18 if MV.props.cell_type == TRIANGLE else 0),
            }),
            ('CURVE', CELL_CYLINDER_NAME, {
                'show_viewport': ('maze_space_dimension', f'int(var) in ({REP_CYLINDER}, {REP_MEOBIUS}, {REP_TORUS})'),
                'show_render': ('maze_space_dimension', f'int(var) in ({REP_CYLINDER}, {REP_MEOBIUS}, {REP_TORUS})'),
                'object': MV.obj_cylinder,
            }),
            ('CURVE', CELL_TORUS_NAME, {
                'show_viewport': ('maze_space_dimension', "int(var) == " + REP_TORUS),
                'show_render': ('maze_space_dimension', "int(var) == " + REP_TORUS),
                'object': MV.obj_torus,
                'deform_axis': 'POS_Y',
            }),
            ('WELD', CELL_WELD_CYLINDER_NAME, {
                'show_viewport': ('maze_space_dimension', f'int(var) in ({REP_CYLINDER}, {REP_MEOBIUS}, {REP_TORUS})'),
                'show_render': ('maze_space_dimension', f'int(var) in ({REP_CYLINDER}, {REP_MEOBIUS}, {REP_TORUS})'),
                'merge_threshold': 0.05,
            }),
            ('DECIMATE', CELL_DECIMATE_NAME, {
                'show_viewport': ('cell_decimate', 'var > 0'),
                'show_render': ('cell_decimate', 'var > 0'),
                'ratio': ('cell_decimate', '1 - var / 100'),
            }),
            ('SUBSURF', CELL_SUBSURF_NAME, {
                'levels': 0,
            }),
            ('DECIMATE', CELL_DECIMATE_PLANAR_NAME, {
                'show_viewport': ('cell_inset', 'var > 0'),
                'show_render': ('cell_inset', 'var > 0'),
                'decimate_type': 'DISSOLVE',
                'angle_limit': 0.5,
            }),
            ('BEVEL', CELL_BEVEL_NAME, {
                'segments': ('cell_contour_black', '2 if var else 4'),
                'limit_method': 'ANGLE',
                'material': ('cell_contour_black', '1 if var else 0'),
                'profile': ('cell_contour_black', '1 if var else 0.5'),
                'angle_limit': 0.75,
                'use_clamp_overlap': False,
                'width': 0,
            }),
            ('WIREFRAME', CELL_WIREFRAME_NAME, {
                'use_replace': False,
                'material_offset': ('cell_contour_black', None),
                'thickness': 0,
            }),
        )
    }

    for obj, mod_params in mod_dic.items():
        for params in mod_params:
            params[2]['show_expanded'] = False
            add_modifier(obj=obj, mod_type=params[0], mod_name=params[1], properties=params[2], overwrite_props=ow, scene=MV.scene)

    generate_drivers(MV, ow)


def add_modifier(obj, mod_type, mod_name, remove_if_already_exists=False, remove_all_modifiers=False, properties=None, overwrite_props=True, scene=None):
    mod_name = mod_name if mod_name != "" else "Fallback"

    if obj is not None:
        mod = None
        if remove_all_modifiers:
            obj.modifiers.clear()

        if mod_name in obj.modifiers:
            if remove_if_already_exists:
                obj.modifiers.remove(obj.modifiers.get(mod_name))
                add_modifier(obj, mod_type, mod_name, remove_if_already_exists, remove_all_modifiers, properties)
            else:
                mod = obj.modifiers[mod_name]
        else:
            mod = obj.modifiers.new(mod_name, mod_type)
            if mod and type(properties) is dict and overwrite_props:
                for prop, value in properties.items():
                    if hasattr(mod, prop):
                        if type(value) is tuple:
                            add_driver_to(obj.modifiers[mod_name], prop, 'var', 'SCENE', scene, 'mg_props.' + value[0], expression=value[1])
                        else:
                            setattr(mod, prop, value)


def add_driver_to(obj, obj_prop, var_name, id_type, _id, prop_path, expression=None):
    add_driver_to_vars(obj, obj_prop, ((var_name, id_type, _id, prop_path),), expression)


def add_driver_to_vars(obj, obj_prop, variables, expression=None):
    """
    Add a driver to obj's obj_prop property

    Each var must be under the form : (var_name, id_type, _id, prop_path)"""
    if obj:
        driver = obj.driver_add(obj_prop).driver
        for i, var_prop in enumerate(variables):
            try:
                var = driver.variables[i]
            except IndexError:
                var = driver.variables.new()
            var.name = var_prop[0]
            var.type = 'SINGLE_PROP'

            target = var.targets[0]
            target.id_type = var_prop[1]
            target.id = var_prop[2]
            target.data_path = str(var_prop[3])

        if expression:
            driver.expression = expression
        else:
            driver.expression = variables[0][0]
