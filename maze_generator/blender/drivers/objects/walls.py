"""
Stores all the drivers used in the walls object
"""

from ..methods import (
    copy_mod2mod_driver,
    setup_mod2mod_driver,
    setup_driver_from_addon_props,
)
from maze_generator.module.space_representation.constants import SpaceRepresentation as sr


def setup_drivers(scene, props):
    names = props.mod_names
    obj_walls = props.objects.walls
    obj_cells = props.objects.cells
    for show in ("show_render", "show_viewport"):
        copy_mod2mod_driver(obj_cells, names.mask_longest_path, show, obj_walls)
        setup_mod2mod_driver(obj_walls, names.mask, "threshold", obj_walls, names.mask, show, "var < 1")
        setup_mod2mod_driver(obj_cells, names.stairs, "strength", obj_walls, names.stairs, show, "var != 0")
        setup_mod2mod_driver(obj_walls, names.solid, "thickness", obj_walls, names.solid, show, "var != 0")
        setup_mod2mod_driver(obj_walls, names.bevel, "width", obj_walls, names.bevel, show, "var > 0")
        setup_mod2mod_driver(
            obj_cells, names.thickness_shrinkwrap, "show_viewport", obj_walls, names.thickness_shrinkwrap, show
        )
        setup_mod2mod_driver(obj_cells, names.texture_disp, "strength", obj_walls, names.texture_disp, show, "var != 0")

        setup_driver_from_addon_props(
            obj_walls, names.torus, show, scene, "space_rep_props.representation", "int(var) == " + sr.TORUS.value
        )
        setup_driver_from_addon_props(
            obj_walls,
            names.cylinder,
            show,
            scene,
            "space_rep_props.representation",
            f"int(var) in ({sr.CYLINDER.value}, {sr.MOEBIUS.value}, {sr.TORUS.value})",
        )
        setup_driver_from_addon_props(
            obj_walls, names.moebius, show, scene, "space_rep_props.representation", f"int(var) == {sr.MOEBIUS.value}"
        )
        setup_driver_from_addon_props(
            obj_walls,
            names.weave_disp,
            show,
            scene,
            "space_rep_props.representation",
            f"int(var) == {sr.CYLINDER.value} or int(var) == {sr.MOEBIUS.value}",
        )
        setup_driver_from_addon_props(obj_walls, names.thickness_disp, show, scene, "maze_basement", "not var")

    copy_mod2mod_driver(obj_cells, names.mask, "threshold", obj_walls)
    copy_mod2mod_driver(obj_cells, names.stairs, "strength", obj_walls)
    copy_mod2mod_driver(obj_cells, names.thickness_disp, "strength", obj_walls)
    copy_mod2mod_driver(obj_cells, names.texture_disp, "strength", obj_walls)

    setup_driver_from_addon_props(obj_walls, names.weave_disp, "strength", scene, "wall_height", "-var")
    setup_driver_from_addon_props(obj_walls, names.bevel, "harden_normals", scene, "meshes.use_smooth", "var")
    setup_driver_from_addon_props(obj_walls, names.screw, "use_smooth_shade", scene, "wall_bevel", "var > 0.005")
