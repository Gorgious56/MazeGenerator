"""
Stores the walls object's modifier properties
"""


import math
from ..methods import add_modifier, ModifierCreator
from ... import meshes as cv
from ....maze_logic.cells import TRIANGLE


def setup_modifiers(scene, props) -> None:
    names = props.mod_names
    ow = props.auto_overwrite
    obj_walls = props.objects.walls
    obj_cells = props.objects.cells
    obj_cylinder = props.objects.cylinder
    obj_torus = props.objects.torus
    obj_thickness_shrinkwrap = props.objects.thickness_shrinkwrap
    tex_disp = props.textures.displacement

    modifiers = []

    if ow or not obj_walls.modifiers.get(names.mask_longest_path):
        modifiers.append(ModifierCreator(
            _type='MASK',
            name=names.mask_longest_path,
            properties={
                "vertex_group": cv.VG_LONGEST_PATH,
                "invert_vertex_group": True,
            }
        ))
    if ow or not obj_walls.modifiers.get(names.mask_sparse):
        modifiers.append(ModifierCreator(
            _type='MASK',
            name=names.mask_sparse,
            properties={
                "vertex_group": cv.VG_STAIRS,
                "threshold": 0,
            }
        ))
    if ow or not obj_walls.modifiers.get(names.mask):
        modifiers.append(
            ModifierCreator(
                _type='MASK',
                name=names.mask,
                properties={
                    "vertex_group": cv.VG_STAIRS,
                    "invert_vertex_group": True,
                }
            ))
    if ow or not obj_walls.modifiers.get(names.stairs):
        modifiers.append(
            ModifierCreator(
                _type='DISPLACE',
                name=names.stairs,
                properties={
                    "direction": 'Z',
                    "vertex_group": cv.VG_STAIRS,
                    'mid_level': 0,
                }
            ))
    if ow or not obj_walls.modifiers.get(names.weld):
        modifiers.append(
            ModifierCreator(
                _type='WELD',
                name=names.weld,
                properties={}
            ))
    if ow or not obj_walls.modifiers.get(names.screw):
        modifiers.append(
            ModifierCreator(
                _type='SCREW',
                name=names.screw,
                properties={
                    'angle': 0,
                    'steps': 1,
                    'render_steps': 1,
                    'screw_offset': 0.3,
                }
            ))
    if ow or not obj_walls.modifiers.get(names.vert_weight_prox):
        modifiers.append(
            ModifierCreator(
                _type='VERTEX_WEIGHT_PROXIMITY',
                name=names.vert_weight_prox,
                properties={
                    'vertex_group': cv.VG_THICKNESS,
                    'target': obj_cells,
                    'proximity_mode': 'GEOMETRY',
                    'proximity_geometry': {'VERTEX'},
                    'falloff_type': 'STEP',
                    'min_dist': 0.001,
                    'max_dist': 0,
                }
            ))
    if ow or not obj_walls.modifiers.get(names.solid):
        modifiers.append(
            ModifierCreator(
                _type='SOLIDIFY',
                name=names.solid,
                properties={
                    'solidify_mode': 'NON_MANIFOLD',
                    'thickness': 0.1,
                    'offset': 0,
                }
            ))
    if ow or not obj_walls.modifiers.get(names.thickness_disp):
        modifiers.append(
            ModifierCreator(
                _type='DISPLACE',
                name=names.thickness_disp,
                properties={
                    'direction': 'Z',
                    'vertex_group': cv.VG_THICKNESS,
                    'mid_level': 0,
                }
            ))
    if ow or not obj_walls.modifiers.get(names.thickness_shrinkwrap):
        modifiers.append(
            ModifierCreator(
                _type='SHRINKWRAP',
                name=names.thickness_shrinkwrap,
                properties={
                    'vertex_group': cv.VG_THICKNESS,
                    'wrap_method': 'PROJECT',
                    'use_project_x': False,
                    'use_project_y': False,
                    'use_project_z': True,
                    'use_negative_direction': True,
                    'use_positive_direction': True,
                    'target': obj_thickness_shrinkwrap,
                }
            ))
    if ow or not obj_walls.modifiers.get(names.bevel):
        modifiers.append(
            ModifierCreator(
                _type='BEVEL',
                name=names.bevel,
                properties={
                    'segments': 4,
                    'limit_method': 'ANGLE',
                    'use_clamp_overlap': True,
                    'width': 0,
                }
            ))
    if ow or not obj_walls.modifiers.get(names.weave_disp):
        modifiers.append(
            ModifierCreator(
                _type='DISPLACE',
                name=names.weave_disp,
                properties={
                    'direction': 'Z',
                    'mid_level': 0.5,
                }
            ))
    if ow or not obj_walls.modifiers.get(names.moebius):
        modifiers.append(
            ModifierCreator(
                _type='SIMPLE_DEFORM',
                name=names.moebius,
                properties={
                    'angle': 2 * math.pi + (1 / 16 if props.cell_type == TRIANGLE else 0),
                }
            ))
    if ow or not obj_walls.modifiers.get(names.cylinder):
        modifiers.append(
            ModifierCreator(
                _type='CURVE',
                name=names.cylinder,
                properties={
                    'object': obj_cylinder,
                }
            ))
    if ow or not obj_walls.modifiers.get(names.torus):
        modifiers.append(
            ModifierCreator(
                _type='CURVE',
                name=names.torus,
                properties={
                    'object': obj_torus,
                    'deform_axis': 'POS_Y',
                }
            ))
    if ow or not obj_walls.modifiers.get(names.texture_disp):
        modifiers.append(
            ModifierCreator(
                _type='DISPLACE',
                name=names.texture_disp,
                properties={
                    'texture': tex_disp,
                    'direction': 'Z',
                }
            ))

    for mod_creator in modifiers:
        mod_creator.object = obj_walls
        mod_creator.set_property("show_expanded", False)
        add_modifier(creator=mod_creator, overwrite_props=ow)
