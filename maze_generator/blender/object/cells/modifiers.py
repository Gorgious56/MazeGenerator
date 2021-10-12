"""
Stores the cells object's modifier properties
"""


import math
from maze_generator.blender.modifier.helper import (
    add_modifier,
    ModifierCreator,
)
import maze_generator.blender.mesh.constants as cv
from maze_generator.maze.cell.constants import CellType


def setup_modifiers(scene, props) -> None:
    names = props.mod_names
    ow = props.generation.auto_overwrite
    obj_cells = props.objects.cells
    obj_cylinder = props.objects.cylinder
    obj_torus = props.objects.torus
    obj_thickness_shrinkwrap = props.objects.thickness_shrinkwrap
    tex_disp = props.textures.displacement

    modifiers = [
        ModifierCreator(
            _type="MASK",
            name=names.mask_longest_path,
            properties={
                "show_viewport": False,
                "vertex_group": cv.VG_LONGEST_PATH,
                "invert_vertex_group": True,
            },
        ),
        ModifierCreator(
            _type="MASK",
            name=names.mask_sparse,
            properties={
                "vertex_group": cv.VG_STAIRS,
            },
        ),
        ModifierCreator(
            _type="MASK",
            name=names.mask,
            properties={
                "vertex_group": cv.VG_STAIRS,
                "invert_vertex_group": True,
                "threshold": 1,
            },
        ),
        ModifierCreator(
            _type="DISPLACE",
            name=names.stairs,
            properties={
                "direction": "Z",
                "vertex_group": cv.VG_STAIRS,
                "mid_level": 0,
                "strength": 0,
            },
        ),
        ModifierCreator(
            _type="SOLIDIFY",
            name=names.thickness_solid,
            properties={
                "thickness": 0.000000001,
                "shell_vertex_group": cv.VG_THICKNESS,
            },
        ),
        ModifierCreator(
            _type="DISPLACE",
            name=names.thickness_disp,
            properties={
                "direction": "Z",
                "vertex_group": cv.VG_THICKNESS,
                "mid_level": 0,
                "strength": 0,
            },
        ),
        ModifierCreator(
            _type="SHRINKWRAP",
            name=names.thickness_shrinkwrap,
            properties={
                "wrap_method": "PROJECT",
                "vertex_group": cv.VG_THICKNESS,
                "use_project_x": False,
                "use_project_y": False,
                "use_project_z": True,
                "use_negative_direction": True,
                "use_positive_direction": True,
                "target": obj_thickness_shrinkwrap,
            },
        ),
        ModifierCreator(
            _type="SIMPLE_DEFORM",
            name=names.moebius,
            properties={
                "angle": 2 * math.pi + (1 / 18 if props.cell_props.is_a(CellType.TRIANGLE) else 0),
            },
        ),
        ModifierCreator(
            _type="CURVE",
            name=names.cylinder,
            properties={
                "object": obj_cylinder,
            },
        ),
        ModifierCreator(
            _type="CURVE",
            name=names.torus,
            properties={
                "object": obj_torus,
                "deform_axis": "POS_Y",
            },
        ),
        ModifierCreator(
            _type="DISPLACE",
            name=names.texture_disp,
            properties={
                "texture": tex_disp,
                "direction": "Z",
                "strength": 0,
            },
        ),
        ModifierCreator(_type="DECIMATE", name=names.decimate, properties={}),
        ModifierCreator(
            _type="SUBSURF",
            name=names.subdiv,
            properties={
                "levels": 0,
            },
        ),
        ModifierCreator(
            _type="BEVEL",
            name=names.bevel,
            properties={
                "limit_method": "ANGLE",
                "angle_limit": 0.75,
                "width": 0,
            },
        ),
        ModifierCreator(
            _type="WIREFRAME",
            name=names.wireframe,
            properties={
                "use_replace": False,
                "thickness": 0,
            },
        ),
    ]

    for mod_creator in modifiers:
        mod_creator.object = obj_cells
        mod_creator.set_property("show_expanded", False)
        add_modifier(creator=mod_creator, overwrite_props=ow or not obj_cells.modifiers.get(mod_creator.name))
