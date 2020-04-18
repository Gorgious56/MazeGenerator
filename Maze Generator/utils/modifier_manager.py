
import math
from ..visual import space_rep_manager as sp_rep
from ..visual import cell_visual as cv
from ..visual.cell_type_manager import POLAR, SQUARE, TRIANGLE, HEXAGON

M_WELD = 'MG_WELD'
M_WELD_2 = 'MG_WELD_2'
M_SCREW = 'MG_SCREW'
M_SOLID = 'MG_SOLIDIFY'
M_BEVEL = 'MG_BEVEL'
M_THICKNESS_SOLID = 'MG_THICK_SOLID'
M_WEAVE_MIX = 'MG_WEAVE_MIX'
M_THICKNESS_DISP = 'MG_THICK_DISP'
M_DECIMATE = 'MG_DECIMATE'
M_DECIMATE_PLANAR = 'MG_DECIMATE_PLANAR'
M_SUBDIV = 'MG_SUBSURF'
M_WIREFRAME = 'MG_WIREFRAME'
M_WEAVE_DISP = 'MG_WEAVE_DISPLACE'
M_CYLINDER = 'MG_CYLINDER'
M_CYLINDER_WELD = 'MG_CYLINDER_WELD'
M_MOEBIUS = 'MG_MOEBIUS'
M_TORUS = 'MG_TORUS'
M_STAIRS = 'MG_STAIRS'
M_TEXTURE_DISP = 'MG_TEX_DISP'
M_MASK = 'MG_MASK_STAIRS'

VISIBILIY = 'VISIBILITY'


def generate_drivers(MV):
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
            ('MASK', M_MASK, {
                VISIBILIY: (MV.obj_walls, MV.obj_walls, 'threshold', M_MASK, M_MASK, 'var < 1'),
                'vertex_group': cv.VG_STAIRS,
                'invert_vertex_group': True,
                'threshold': (MV.obj_cells, MV.obj_walls, 'threshold', M_MASK, M_MASK, 'var'),
            }),
            ('DISPLACE', M_STAIRS, {
                VISIBILIY: (MV.obj_cells, MV.obj_walls, 'strength', M_STAIRS, M_STAIRS, 'var != 0'),
                'strength': (MV.obj_cells, MV.obj_walls, 'strength', M_STAIRS, M_STAIRS, 'var'),
                'direction': 'Z',
                'vertex_group': cv.VG_STAIRS,
                'mid_level': 0,
            }),
            ('WELD', M_WELD, {
                'merge_threshold': (MV.obj_cells, MV.obj_walls, 'merge_threshold', M_WELD, M_WELD, 'var'),
            }),
            ('SCREW', M_SCREW, {
                'angle': 0,
                'steps': 1,
                'render_steps': 1,
                'screw_offset': 0.5,
                'use_smooth_shade': ('wall_bevel', 'var > 0.005'),
            }),
            ('SOLIDIFY', M_SOLID, {
                VISIBILIY: (MV.obj_walls, MV.obj_walls, 'thickness', M_SOLID, M_SOLID, 'var != 0'),
                'solidify_mode': 'NON_MANIFOLD',
                'thickness': 0.2,
                'offset': 0,
            }),
            ('BEVEL', M_BEVEL, {
                VISIBILIY: (MV.obj_walls, MV.obj_walls, 'width', M_BEVEL, M_BEVEL, 'var > 0'),
                'segments': 4,
                'limit_method': 'ANGLE',
                'use_clamp_overlap': True,
                'width': 0,
            }),
            ('DISPLACE', M_WEAVE_DISP, {
                VISIBILIY: ('maze_space_dimension', 'int(var) == ' + sp_rep.REP_CYLINDER + ' or int(var) == ' + sp_rep.REP_MEOBIUS),
                'strength': ('wall_height', '-var'),
                'direction': 'Z',
                'mid_level': 0.5,
            }),
            ('SIMPLE_DEFORM', M_MOEBIUS, {
                VISIBILIY: ('maze_space_dimension', 'int(var) == ' + sp_rep.REP_MEOBIUS),
                'angle': 2 * math.pi + (1 / 16 if MV.props.cell_type == TRIANGLE else 0),
            }),
            ('CURVE', M_CYLINDER, {
                VISIBILIY: ('maze_space_dimension', f'int(var) in ({sp_rep.REP_CYLINDER}, {sp_rep.REP_MEOBIUS}, {sp_rep.REP_TORUS})'),
                'object': MV.obj_cylinder,
            }),
            ('CURVE', M_TORUS, {
                VISIBILIY: ('maze_space_dimension', 'int(var) == ' + sp_rep.REP_TORUS),
                'object': MV.obj_torus,
                'deform_axis': 'POS_Y',
            }),
            ('WELD', M_CYLINDER_WELD, {
                VISIBILIY: ('maze_space_dimension', sp_rep.REP_BOX + " > int(var) > " + sp_rep.REP_REGULAR),
                'merge_threshold': 0.1,
            }),
            ('DISPLACE', M_TEXTURE_DISP, {
                VISIBILIY: (MV.obj_cells, MV.obj_walls, 'strength', M_TEXTURE_DISP, M_TEXTURE_DISP, 'var != 0'),
                'strength': (MV.obj_cells, MV.obj_walls, 'strength', M_TEXTURE_DISP, M_TEXTURE_DISP, 'var'),
                'texture': MV.tex_disp,
                'direction': 'Z',
            }),
        ),
        MV.obj_cells: (
            ('MASK', M_MASK, {
                VISIBILIY: (MV.obj_cells, MV.obj_cells, 'threshold', M_MASK, M_MASK, 'var < 1'),
                'vertex_group': cv.VG_STAIRS,
                'invert_vertex_group': True,
                'threshold': 1,
            }),
            ('DISPLACE', M_STAIRS, {
                VISIBILIY: (MV.obj_cells, MV.obj_cells, 'strength', M_STAIRS, M_STAIRS, 'var != 0'),
                'direction': 'Z',
                'vertex_group': cv.VG_STAIRS,
                'mid_level': 0, 'strength': 0,
            }),
            ('WELD', M_WELD, {
                VISIBILIY: ('cell_inset', 'var == 0'),
                'vertex_group': cv.VG_DISPLACE,
                'invert_vertex_group': True,
                'merge_threshold': 0.04,
            }),
            ('WELD', M_WELD_2, {
                VISIBILIY: ('maze_weave', 'var != 0'),
                'vertex_group': cv.VG_DISPLACE,
                'invert_vertex_group': False,
            }),
            ('SOLIDIFY', M_THICKNESS_SOLID, {
                VISIBILIY: (MV.obj_cells, MV.obj_cells, 'thickness', M_THICKNESS_SOLID, M_THICKNESS_SOLID, 'var != 0'),
                'thickness': .000000001,
                'shell_vertex_group': cv.VG_THICKNESS
            }),
            ('VERTEX_WEIGHT_MIX', M_WEAVE_MIX, {
                VISIBILIY: ('maze_weave', "var"),
                'vertex_group_a': cv.VG_THICKNESS,
                'vertex_group_b': cv.VG_DISPLACE,
                'mix_mode': 'ADD',
                'mix_set': 'B',
                'mask_constant': 0.97,
            }),
            ('DISPLACE', M_THICKNESS_DISP, {
                'direction': 'Z',
                'vertex_group': cv.VG_THICKNESS,
                'mid_level': 0,
                'strength': 0,
            }),
            ('DISPLACE', M_WEAVE_DISP, {
                VISIBILIY: ('maze_weave', "var"),
                'direction': 'Z',
                'vertex_group': cv.VG_DISPLACE,
                'mid_level': 0,
                'strength': 0.2
            }),
            ('SIMPLE_DEFORM', M_MOEBIUS, {
                VISIBILIY: ('maze_space_dimension', "int(var) == " + sp_rep.REP_MEOBIUS),
                'angle': 2 * math.pi + (1 / 18 if MV.props.cell_type == TRIANGLE else 0),
            }),
            ('CURVE', M_CYLINDER, {
                VISIBILIY: ('maze_space_dimension', f'int(var) in ({sp_rep.REP_CYLINDER}, {sp_rep.REP_MEOBIUS}, {sp_rep.REP_TORUS})'),
                'object': MV.obj_cylinder,
            }),
            ('CURVE', M_TORUS, {
                VISIBILIY: ('maze_space_dimension', "int(var) == " + sp_rep.REP_TORUS),
                'object': MV.obj_torus,
                'deform_axis': 'POS_Y',
            }),
            ('WELD', M_CYLINDER_WELD, {
                VISIBILIY: ('maze_space_dimension', f'int(var) in ({sp_rep.REP_CYLINDER}, {sp_rep.REP_MEOBIUS}, {sp_rep.REP_TORUS})'),
                'merge_threshold': 0.05,
                'vertex_group': cv.VG_DISPLACE,
                'invert_vertex_group': True
            }),
            ('DISPLACE', M_TEXTURE_DISP, {
                VISIBILIY: (MV.obj_cells, MV.obj_cells, 'strength', M_TEXTURE_DISP, M_TEXTURE_DISP, 'var != 0'),
                'texture': MV.tex_disp,
                'direction': 'Z',
                'strength': 0,
            }),
            ('DECIMATE', M_DECIMATE, {
                VISIBILIY:
                (
                    MV.obj_cells,
                    M_DECIMATE,
                    (
                        ('cell_deci', 'SCENE', MV.scene, 'mg_props.cell_decimate'),
                        ('cell_inset', 'SCENE', MV.scene, 'mg_props.cell_inset'),
                    ),
                    'cell_deci > 0 and cell_inset > 0',
                ),
                'ratio': ('cell_decimate', '1 - var / 100'),
            }),
            ('SUBSURF', M_SUBDIV, {             
                VISIBILIY: (MV.obj_cells, MV.obj_cells, 'levels', M_SUBDIV, M_SUBDIV, 'var > 0'),
                'render_levels': (MV.obj_cells, MV.obj_cells, 'levels', M_SUBDIV, M_SUBDIV, 'var'),
                'levels': 0,
            }),
            ('DECIMATE', M_DECIMATE_PLANAR, {
                VISIBILIY:
                (
                    MV.obj_cells,
                    M_DECIMATE_PLANAR,
                    (
                        ('subdiv', 'OBJECT', MV.obj_cells, 'modifiers["' + M_SUBDIV + '"].levels'),
                        ('cell_inset', 'SCENE', MV.scene, 'mg_props.cell_inset'),
                    ),
                    'subdiv == 0 and cell_inset > 0',
                ),
                'decimate_type': 'DISSOLVE',
                'angle_limit': ('cell_type', f'0.02 if var == {int(POLAR)} or var != {int(sp_rep.REP_REGULAR)} else 0.43'),
            }),
            ('BEVEL', M_BEVEL, {
                VISIBILIY: (MV.obj_cells, MV.obj_cells, 'width', M_BEVEL, M_BEVEL, 'var != 0'),
                'segments': ('cell_contour_black', '2 if var else 4'),
                'limit_method': 'ANGLE',
                'material': ('cell_contour_black', '1 if var else 0'),
                'profile': ('cell_contour_black', '1 if var else 0.5'),
                'angle_limit': 0.75,
                'use_clamp_overlap': False,
                'width': 0,
            }),
            ('WIREFRAME', M_WIREFRAME, {
                VISIBILIY: (MV.obj_cells, MV.obj_cells, 'thickness', M_WIREFRAME, M_WIREFRAME, 'var != 0'),
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

    generate_drivers(MV)


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
                    if type(value) is tuple:
                        if type(value[0]) is not str:
                            if type(value[2]) is tuple:
                                if prop == VISIBILIY:
                                    add_driver_to_vars(value[0].modifiers[value[1]], 'show_render', value[2], value[3])
                                    add_driver_to_vars(value[0].modifiers[value[1]], 'show_viewport', value[2], value[3])
                                else:
                                    add_driver_to_vars(value[0].modifiers[value[1]], prop, value[2], value[3])
                            else:
                                if prop == VISIBILIY:
                                    add_driver_to(value[1].modifiers[value[4]], 'show_render', 'var', 'OBJECT', value[0], 'modifiers["' + value[3] + '"].' + value[2], value[5])
                                    add_driver_to(value[1].modifiers[value[4]], 'show_viewport', 'var', 'OBJECT', value[0], 'modifiers["' + value[3] + '"].' + value[2], value[5])
                                else:
                                    add_driver_to(value[1].modifiers[value[4]], prop, 'var', 'OBJECT', value[0], 'modifiers["' + value[3] + '"].' + value[2], value[5])
                        else:
                            if prop == VISIBILIY:
                                add_driver_to(obj.modifiers[mod_name], 'show_render', 'var', 'SCENE', scene, 'mg_props.' + value[0], expression=value[1])
                                add_driver_to(obj.modifiers[mod_name], 'show_viewport', 'var', 'SCENE', scene, 'mg_props.' + value[0], expression=value[1])
                            else:
                                add_driver_to(obj.modifiers[mod_name], prop, 'var', 'SCENE', scene, 'mg_props.' + value[0], expression=value[1])
                    elif hasattr(mod, prop):
                        setattr(mod, prop, value)


def add_driver_to(obj, prop_to, var_name, id_type, _id, prop_from, expression=None):
    add_driver_to_vars(obj, prop_to, ((var_name, id_type, _id, prop_from),), expression)


def add_driver_to_vars(obj, prop_to, variables, expression=None):
    """
    Add a driver to obj's prop_to property

    Each var must be under the form : (var_name, id_type, _id, prop_from)"""
    if obj:
        driver = obj.driver_add(prop_to).driver
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
