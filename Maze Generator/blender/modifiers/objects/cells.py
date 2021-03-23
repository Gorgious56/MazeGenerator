"""
Stores the cells object's modifier properties
"""


import math
from ..methods import add_modifier, ModifierCreator
from ... import meshes as cv
from ....maze_logic.cells import CellType


def setup_modifiers(scene, props) -> None:
    names = props.mod_names
    ow = props.auto_overwrite
    obj_cells = props.objects.cells
    obj_cylinder = props.objects.cylinder
    obj_torus = props.objects.torus
    obj_thickness_shrinkwrap = props.objects.thickness_shrinkwrap
    tex_disp = props.textures.displacement

    modifiers = []

    if ow or not obj_cells.modifiers.get(names.mask_longest_path):
        modifiers.append(
            ModifierCreator(
                _type='MASK',
                name=names.mask_longest_path,
                properties={
                    "show_viewport": False,
                    "vertex_group": cv.VG_LONGEST_PATH,
                    "invert_vertex_group": True,
                }
            ))
    if ow or not obj_cells.modifiers.get(names.mask_sparse):
        modifiers.append(
            ModifierCreator(
                _type='MASK',
                name=names.mask_sparse,
                properties={
                    "vertex_group": cv.VG_STAIRS,
                }
            ))
    if ow or not obj_cells.modifiers.get(names.mask):
        modifiers.append(ModifierCreator(
            _type='MASK',
            name=names.mask,
            properties={
                "vertex_group": cv.VG_STAIRS,
                "invert_vertex_group": True,
                "threshold": 1,
            }
        ))
    if ow or not obj_cells.modifiers.get(names.stairs):
        modifiers.append(ModifierCreator(
            _type='DISPLACE',
            name=names.stairs,
            properties={
                "direction": 'Z',
                "vertex_group": cv.VG_STAIRS,
                "mid_level": 0,
                "strength": 0,
            }
        ))
    if ow or not obj_cells.modifiers.get(names.thickness_solid):
        modifiers.append(
            ModifierCreator(
                _type='SOLIDIFY',
                name=names.thickness_solid,
                properties={
                    "thickness": .000000001,
                    "shell_vertex_group": cv.VG_THICKNESS,
                }
            ))
    if ow or not obj_cells.modifiers.get(names.thickness_disp):
        modifiers.append(
            ModifierCreator(
                _type='DISPLACE',
                name=names.thickness_disp,
                properties={
                    "direction": 'Z',
                    "vertex_group": cv.VG_THICKNESS,
                    "mid_level": 0,
                    "strength": 0,
                }
            ))
    if ow or not obj_cells.modifiers.get(names.thickness_shrinkwrap):
        modifiers.append(
            ModifierCreator(
                _type='SHRINKWRAP',
                name=names.thickness_shrinkwrap,
                properties={
                    "wrap_method": 'PROJECT',
                    "vertex_group": cv.VG_THICKNESS,
                    "use_project_x": False,
                    "use_project_y": False,
                    "use_project_z": True,
                    "use_negative_direction": True,
                    "use_positive_direction": True,
                    "target": obj_thickness_shrinkwrap,
                }
            ))
    if ow or not obj_cells.modifiers.get(names.moebius):
        modifiers.append(
            ModifierCreator(
                _type='SIMPLE_DEFORM',
                name=names.moebius,
                properties={
                    "angle": 2 * math.pi +
                (1 / 18 if props.is_cell_type(CellType.TRIANGLE) else 0),
                }
            ))
    if ow or not obj_cells.modifiers.get(names.cylinder):
        modifiers.append(
            ModifierCreator(
                _type='CURVE',
                name=names.cylinder,
                properties={
                    "object": obj_cylinder,
                }
            ))
    if ow or not obj_cells.modifiers.get(names.torus):
        modifiers.append(
            ModifierCreator(
                _type='CURVE',
                name=names.torus,
                properties={
                    "object": obj_torus,
                    "deform_axis": 'POS_Y',
                }
            ))
    if ow or not obj_cells.modifiers.get(names.texture_disp):
        modifiers.append(
            ModifierCreator(
                _type='DISPLACE',
                name=names.texture_disp,
                properties={
                    "texture": tex_disp,
                    "direction": 'Z',
                    "strength": 0,
                }
            ))
    if ow or not obj_cells.modifiers.get(names.decimate):
        modifiers.append(
            ModifierCreator(
                _type='DECIMATE',
                name=names.decimate,
                properties={}
            ))
    if ow or not obj_cells.modifiers.get(names.subdiv):
        modifiers.append(
            ModifierCreator(
                _type='SUBSURF',
                name=names.subdiv,
                properties={
                    "levels": 0,
                }
            ))
    if ow or not obj_cells.modifiers.get(names.bevel):
        modifiers.append(
            ModifierCreator(
                _type='BEVEL',
                name=names.bevel,
                properties={
                    "limit_method": 'ANGLE',
                    "angle_limit": 0.75,
                    "width": 0,
                }
            ))
    if ow or not obj_cells.modifiers.get(names.wireframe):
        modifiers.append(
            ModifierCreator(
                _type='WIREFRAME',
                name=names.wireframe,
                properties={
                    "use_replace": False,
                    "thickness": 0,
                }
            ))

    for mod_creator in modifiers:
        mod_creator.object = obj_cells
        mod_creator.set_property('show_expanded', False)
        add_modifier(creator=mod_creator, overwrite_props=ow)
