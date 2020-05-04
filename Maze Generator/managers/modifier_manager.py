
import bpy.types as bpy_types
import math
from . import space_rep_manager as sp_rep
from . import mesh_manager as cv
from .cell_type_manager import SQUARE, TRIANGLE, HEXAGON

M_WELD = 'MG_WELD'
M_WELD_2 = 'MG_WELD_2'
M_SCREW = 'MG_SCREW'
M_SOLID = 'MG_SOLIDIFY'
M_BEVEL = 'MG_BEVEL'
M_THICKNESS_SOLID = 'MG_THICK_SOLID'
M_WEAVE_MIX = 'MG_WEAVE_MIX'
M_THICKNESS_DISP = 'MG_THICK_DISP'
M_THICKNESS_SHRINKWRAP = 'MG_THICK_SHRINKWRAP'
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
M_MASK_SPARSE = 'MG_MASK_SPARSE'
M_MASK_LONGEST_PATH = 'MG_MASK_PATH'
M_VERT_WEIGHT_PROX = 'MG_WEIGHT_PROX'
M_SMOOTH_CENTER_NAME = 'MG_SMOOTH_CENTER'
M_SMOOTH_BRIDGE_COL_X_NAME, M_SMOOTH_BRIDGE_COL_Y_NAME = 'MG_SMOOTH_BRIDGE_COL_X', 'MG_SMOOTH_BRIDGE_COL_Y'
M_SMOOTH_BRIDGE_ROW_X_NAME, M_SMOOTH_BRIDGE_ROW_Y_NAME = 'MG_SMOOTH_BRIDGE_ROW_X', 'MG_SMOOTH_BRIDGE_ROW_Y'
M_MASK_BRIDGE = 'MG_MASK_BRIDGE'

VISIBILIY = 'VISIBILITY'


def setup_modifiers_and_drivers(MV, OM, TM) -> None:
    ow = MV.props.auto_overwrite or not any(ModifierManager.drivers)
    obj_walls = OM.obj_walls
    obj_cells = OM.obj_cells
    obj_cylinder = OM.obj_cylinder
    obj_torus = OM.obj_torus
    obj_thickness_shrinkwrap = OM.obj_thickness_shrinkwrap
    tex_disp = TM.tex_disp
    scene = MV.scene
    mod_dic = {
        obj_walls: (
            ('MASK', M_MASK_LONGEST_PATH, {
                VISIBILIY: (obj_cells, obj_walls, 'show_viewport', M_MASK_LONGEST_PATH, M_MASK_LONGEST_PATH, 'var'),
                'vertex_group': cv.VG_LONGEST_PATH,
                'invert_vertex_group': True,
            }),
            ('MASK', M_MASK_SPARSE, {
                'vertex_group': cv.VG_STAIRS,
                'threshold': 0
            }),
            ('MASK', M_MASK, {
                VISIBILIY: (obj_walls, obj_walls, 'threshold', M_MASK, M_MASK, 'var < 1'),
                'vertex_group': cv.VG_STAIRS,
                'invert_vertex_group': True,
                'threshold': (obj_cells, obj_walls, 'threshold', M_MASK, M_MASK, 'var'),
            }),
            ('DISPLACE', M_STAIRS, {
                VISIBILIY: (obj_cells, obj_walls, 'strength', M_STAIRS, M_STAIRS, 'var != 0'),
                'strength': (obj_cells, obj_walls, 'strength', M_STAIRS, M_STAIRS, 'var'),
                'direction': 'Z',
                'vertex_group': cv.VG_STAIRS,
                'mid_level': 0,
            }),
            ('WELD', M_WELD, {
            }),
            ('SCREW', M_SCREW, {
                'angle': 0,
                'steps': 1,
                'render_steps': 1,
                'screw_offset': 0.3,
                'use_smooth_shade': ('wall_bevel', 'var > 0.005'),
            }),
            ('VERTEX_WEIGHT_PROXIMITY', M_VERT_WEIGHT_PROX, {
                'vertex_group': cv.VG_THICKNESS,
                'target': obj_cells,
                'proximity_mode': 'GEOMETRY',
                'proximity_geometry': {'VERTEX'},
                'falloff_type': 'STEP',
                'min_dist': 0.001,
                'max_dist': 0,
            }),
            ('SOLIDIFY', M_SOLID, {
                VISIBILIY: (obj_walls, obj_walls, 'thickness', M_SOLID, M_SOLID, 'var != 0'),
                'solidify_mode': 'NON_MANIFOLD',
                'thickness': 0.1,
                'offset': 0,
            }),
            ('DISPLACE', M_THICKNESS_DISP, {
                VISIBILIY: ('maze_basement', 'not var'),
                'direction': 'Z',
                'vertex_group': cv.VG_THICKNESS,
                'mid_level': 0,
                'strength': (obj_cells, obj_walls, 'strength', M_THICKNESS_DISP, M_THICKNESS_DISP, 'var'),
            }),
            ('SHRINKWRAP', M_THICKNESS_SHRINKWRAP, {
                VISIBILIY: ('maze_basement', 'var'),
                'vertex_group': cv.VG_THICKNESS,
                'wrap_method': 'PROJECT',
                'use_project_x': False,
                'use_project_y': False,
                'use_project_z': True,
                'use_negative_direction': True,
                'use_positive_direction': True,
                'target': obj_thickness_shrinkwrap
            }),
            ('BEVEL', M_BEVEL, {
                VISIBILIY: (obj_walls, obj_walls, 'width', M_BEVEL, M_BEVEL, 'var > 0'),
                'segments': 4,
                'limit_method': 'ANGLE',
                'use_clamp_overlap': True,
                'width': 0,
                'harden_normals': ('cell_use_smooth', 'var'),
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
                'object': obj_cylinder,
            }),
            ('CURVE', M_TORUS, {
                VISIBILIY: ('maze_space_dimension', 'int(var) == ' + sp_rep.REP_TORUS),
                'object': obj_torus,
                'deform_axis': 'POS_Y',
            }),
            ('WELD', M_CYLINDER_WELD, {
                VISIBILIY: ('maze_space_dimension', sp_rep.REP_BOX + " > int(var) > " + sp_rep.REP_REGULAR),
                'merge_threshold': 0.1,
            }),
            ('DISPLACE', M_TEXTURE_DISP, {
                VISIBILIY: (obj_cells, obj_walls, 'strength', M_TEXTURE_DISP, M_TEXTURE_DISP, 'var != 0'),
                'strength': (obj_cells, obj_walls, 'strength', M_TEXTURE_DISP, M_TEXTURE_DISP, 'var'),
                'texture': tex_disp,
                'direction': 'Z',
            }),
        ),
        obj_cells: (
            ('MASK', M_MASK_LONGEST_PATH, {
                'show_viewport': False,
                'show_render': (obj_cells, obj_cells, 'show_viewport', M_MASK_LONGEST_PATH, M_MASK_LONGEST_PATH, 'var'),
                'vertex_group': cv.VG_LONGEST_PATH,
                'invert_vertex_group': True,
            }),
            ('MASK', M_MASK_SPARSE, {
                'vertex_group': cv.VG_STAIRS,
            }),            
            ('MASK', M_MASK, {
                VISIBILIY: (obj_cells, obj_cells, 'threshold', M_MASK, M_MASK, 'var < 1'),
                'vertex_group': cv.VG_STAIRS,
                'invert_vertex_group': True,
                'threshold': 1,
            }),
            ('DISPLACE', M_STAIRS, {
                VISIBILIY: (obj_cells, obj_cells, 'strength', M_STAIRS, M_STAIRS, 'var != 0'),
                'direction': 'Z',
                'vertex_group': cv.VG_STAIRS,
                'mid_level': 0, 'strength': 0,
            }),
            # ('WELD', M_WELD_2, {
            #     VISIBILIY: ('maze_weave', 'var != 0'),
            #     'vertex_group': cv.VG_DISPLACE,
            #     'invert_vertex_group': False,
            # }),
            ('SOLIDIFY', M_THICKNESS_SOLID, {
                VISIBILIY: (obj_cells, obj_cells, 'thickness', M_THICKNESS_SOLID, M_THICKNESS_SOLID, 'var != 0'),
                'thickness': .000000001,
                'shell_vertex_group': cv.VG_THICKNESS
            }),
            # ('VERTEX_WEIGHT_MIX', M_WEAVE_MIX, {
            #     VISIBILIY: ('maze_weave', "var"),
            #     'vertex_group_a': cv.VG_THICKNESS,
            #     'vertex_group_b': cv.VG_DISPLACE,
            #     'mix_mode': 'ADD',
            #     'mix_set': 'B',
            #     'mask_constant': 0.97,
            # }),
            ('DISPLACE', M_THICKNESS_DISP, {
                VISIBILIY: ('maze_basement', 'not var'),
                'direction': 'Z',
                'vertex_group': cv.VG_THICKNESS,
                'mid_level': 0,
                'strength': 0,
            }),
            ('SHRINKWRAP', M_THICKNESS_SHRINKWRAP, {
                VISIBILIY: ('maze_basement', 'var'),
                'vertex_group': cv.VG_THICKNESS,
                'wrap_method': 'PROJECT',
                'use_project_x': False,
                'use_project_y': False,
                'use_project_z': True,
                'use_negative_direction': True,
                'use_positive_direction': True,
                'target': obj_thickness_shrinkwrap
            }),
            # ('DISPLACE', M_WEAVE_DISP, {
            #     VISIBILIY: ('maze_weave', "var"),
            #     'direction': 'Z',
            #     'vertex_group': cv.VG_DISPLACE,
            #     'mid_level': 0,
            #     'strength': 0.2
            # }),
            ('SIMPLE_DEFORM', M_MOEBIUS, {
                VISIBILIY: ('maze_space_dimension', "int(var) == " + sp_rep.REP_MEOBIUS),
                'angle': 2 * math.pi + (1 / 18 if MV.props.cell_type == TRIANGLE else 0),
            }),
            ('CURVE', M_CYLINDER, {
                VISIBILIY: ('maze_space_dimension', f'int(var) in ({sp_rep.REP_CYLINDER}, {sp_rep.REP_MEOBIUS}, {sp_rep.REP_TORUS})'),
                'object': obj_cylinder,
            }),
            ('CURVE', M_TORUS, {
                VISIBILIY: ('maze_space_dimension', "int(var) == " + sp_rep.REP_TORUS),
                'object': obj_torus,
                'deform_axis': 'POS_Y',
            }),
            ('WELD', M_CYLINDER_WELD, {
                VISIBILIY: ('maze_space_dimension', f'int(var) in ({sp_rep.REP_CYLINDER}, {sp_rep.REP_MEOBIUS}, {sp_rep.REP_TORUS})'),
                'merge_threshold': 0.05,
                'vertex_group': cv.VG_DISPLACE,
                'invert_vertex_group': True
            }),
            ('DISPLACE', M_TEXTURE_DISP, {
                VISIBILIY: (obj_cells, obj_cells, 'strength', M_TEXTURE_DISP, M_TEXTURE_DISP, 'var != 0'),
                'texture': tex_disp,
                'direction': 'Z',
                'strength': 0,
            }),
            ('DECIMATE', M_DECIMATE, {
                VISIBILIY:
                (
                    obj_cells,
                    M_DECIMATE,
                    (
                        ('cell_deci', 'SCENE', scene, 'mg_props.cell_decimate'),
                        ('cell_inset', 'SCENE', scene, 'mg_props.cell_inset'),
                        ('stairs', 'OBJECT', obj_cells, 'modifiers["' + M_STAIRS + '"].strength'),
                    ),
                    'cell_deci > 0 and (cell_inset > 0 or stairs != 0)',
                ),
                'ratio': ('cell_decimate', '1 - var / 100'),
            }),
            ('SUBSURF', M_SUBDIV, {
                VISIBILIY: (obj_cells, obj_cells, 'levels', M_SUBDIV, M_SUBDIV, 'var > 0'),
                'render_levels': (obj_cells, obj_cells, 'levels', M_SUBDIV, M_SUBDIV, 'var'),
                'levels': 0,
            }),
            ('BEVEL', M_BEVEL, {
                VISIBILIY:
                (
                    obj_cells,
                    M_BEVEL,
                    (
                        ('cell_bevel', 'OBJECT', obj_cells, 'modifiers["' + M_BEVEL + '"].width'),
                        ('cell_inset', 'SCENE', scene, 'mg_props.cell_inset'),
                    ),
                    'cell_bevel != 0 and cell_inset > 0.1',
                ),
                'segments': ('cell_contour_black', '2 if var else 4'),
                'limit_method': 'ANGLE',
                'material': ('cell_contour_black', '1 if var else 0'),
                'profile': ('cell_contour_black', '1 if var else 0.5'),
                'angle_limit': 0.75,
                # 'use_clamp_overlap': False,
                'width': 0,
                'miter_inner': ('cell_contour_black', '2 if var else 0'),
                'miter_outer': ('cell_contour_black', '2 if var else 0'),
            }),
            ('WIREFRAME', M_WIREFRAME, {
                VISIBILIY:
                (
                    obj_cells,
                    M_WIREFRAME,
                    (
                        ('cell_wireframe', 'OBJECT', obj_cells, 'modifiers["' + M_WIREFRAME + '"].thickness'),
                        ('cell_inset', 'SCENE', scene, 'mg_props.cell_inset'),
                    ),
                    'cell_wireframe != 0 and cell_inset > 0.1',
                ),
                # VISIBILIY: (obj_cells, obj_cells, 'thickness', M_WIREFRAME, M_WIREFRAME, 'var != 0'),
                'use_replace': False,
                'material_offset': ('cell_contour_black', None),
                'thickness': 0,
                # 'vertex_group': cv.VG_THICKNESS,
                # 'thickness_vertex_group': ('maze_basement', "not var"),
                # 'invert_vertex_group': True,
            }),
        )
    }

    for obj, mod_params in mod_dic.items():
        for params in mod_params:
            params[2]['show_expanded'] = False
            add_modifier(obj=obj, mod_type=params[0], mod_name=params[1], properties=params[2], overwrite_props=ow, scene=scene)

    if ow:
        add_driver_to_vars(
            obj_thickness_shrinkwrap,
            ('location', 2),
            (
                ('stairs', 'OBJECT', obj_cells, 'modifiers["' + M_STAIRS + '"].strength'),
                ('thickness', 'OBJECT', obj_cells, 'modifiers["' + M_THICKNESS_DISP + '"].strength'),
            ),
            expression='thickness if stairs > 0 else stairs + thickness',
        )

        # Scale the cylinder and torus objects when scaling the size of the maze
        for i, obj in enumerate((obj_cylinder, obj_torus)):
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
                target.id = scene
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


def add_modifier(
        obj: bpy_types.Object, mod_type: str, mod_name: str,
        remove_if_already_exists: bool = False, remove_all_modifiers: bool = False,
        properties=None, overwrite_props: bool = True, scene: bpy_types.Scene = None) -> None:
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


def add_driver_to(obj: bpy_types.Object, prop_to, var_name: str, id_type: str, _id, prop_from, expression: str = None) -> None:
    add_driver_to_vars(obj, prop_to, ((var_name, id_type, _id, prop_from),), expression)


def add_driver_to_vars(obj: bpy_types.Object, prop_to, variables, expression: str = None) -> None:
    """
    Add a driver to obj's prop_to property

    Each var must be under the form : (var_name, id_type, _id, prop_from)"""
    if obj:
        if type(prop_to) is tuple:
            driver = obj.driver_add(prop_to[0], prop_to[1]).driver
        else:
            driver = obj.driver_add(prop_to).driver
            ModifierManager.drivers.append((obj, prop_to))
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


class ModifierManager:
    drivers = []

    def delete_all_drivers():
        for driver_settings in ModifierManager.drivers:
            try:
                driver_settings[0].driver_remove(driver_settings[1])
            except TypeError:
                pass
        ModifierManager.drivers = []
