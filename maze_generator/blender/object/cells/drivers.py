"""
Stores all the drivers used in the cells object
"""

from maze_generator.blender.driver.helper import (
    setup_mod2mod_driver,
    setup_driver_from_addon_props,
    setup_driver,
)
from maze_generator.blender.driver.prop import (
    DriverProperties,
    DriverVariable,
)
from maze_generator.maze.space_representation.constants import SpaceRepresentation as sr


def setup_drivers(scene, props):
    names = props.mod_names
    obj_cells = props.objects.cells
    for show in ("show_render", "show_viewport"):
        setup_mod2mod_driver(obj_cells, names.mask, "threshold", obj_cells, names.mask, show, "var < 1")
        setup_mod2mod_driver(obj_cells, names.stairs, "strength", obj_cells, names.stairs, show, "var != 0")
        setup_mod2mod_driver(obj_cells, names.texture_disp, "strength", obj_cells, names.texture_disp, show, "var != 0")

        setup_driver_from_addon_props(
            obj_cells,
            names.torus,
            show,
            scene,
            "space_rep_props.representation",
            "int(var) == " + sr.TORUS.value,
        )
        setup_driver_from_addon_props(
            obj_cells,
            names.cylinder,
            show,
            scene,
            "space_rep_props.representation",
            f"int(var) in ({sr.CYLINDER.value}, {sr.MOEBIUS.value}, {sr.TORUS.value})",
        )
        setup_driver_from_addon_props(
            obj_cells,
            names.moebius,
            show,
            scene,
            "space_rep_props.representation",
            f"int(var) == {sr.MOEBIUS.value}",
        )

        setup_driver(
            obj_cells.modifiers[names.thickness_disp],
            DriverProperties(
                show,
                [
                    DriverVariable("basement", "SCENE", scene, "maze_basement"),
                    DriverVariable("stairs", "OBJECT", obj_cells, f'modifiers["{names.stairs}"].strength'),
                ],
                expression="not basement or stairs == 0",
            ),
        )

        setup_driver(
            obj_cells.modifiers[names.thickness_solid],
            DriverProperties(
                show,
                [
                    DriverVariable(
                        "sw_visibility", "OBJECT", obj_cells, f'modifiers["{names.thickness_disp}"].show_viewport'
                    ),
                    DriverVariable(
                        "disp_visibility",
                        "OBJECT",
                        obj_cells,
                        f'modifiers["{names.thickness_shrinkwrap}"].show_viewport',
                    ),
                ],
                expression="sw_visibility or disp_visibility",
            ),
        )
        setup_driver(
            obj_cells.modifiers[names.wireframe],
            DriverProperties(
                show,
                [
                    DriverVariable("cell_wireframe", "OBJECT", obj_cells, f'modifiers["{names.wireframe}"].thickness'),
                    DriverVariable("cell_inset", "SCENE", scene, "mg_props.cell_props.inset"),
                ],
                expression="cell_wireframe != 0 and cell_inset > 0.1",
            ),
        )
        setup_driver(
            obj_cells.modifiers[names.bevel],
            DriverProperties(
                show,
                [
                    DriverVariable("cell_bevel", "OBJECT", obj_cells, f'modifiers["{names.bevel}"].width'),
                    DriverVariable("cell_inset", "SCENE", scene, "mg_props.cell_props.inset"),
                ],
                expression="cell_bevel != 0 and cell_inset > 0.1",
            ),
        )
        setup_driver(
            obj_cells.modifiers[names.decimate],
            DriverProperties(
                show,
                [
                    DriverVariable("cell_deci", "SCENE", scene, "mg_props.cell_props.cell_decimate"),
                    DriverVariable("cell_inset", "SCENE", scene, "mg_props.cell_props.inset"),
                    DriverVariable("stairs", "OBJECT", obj_cells, f'modifiers["{names.stairs}"].strength'),
                ],
                expression="cell_deci > 0 and (cell_inset > 0 or stairs != 0)",
            ),
        )
        setup_driver(
            obj_cells.modifiers[names.thickness_shrinkwrap],
            DriverProperties(
                show,
                [
                    DriverVariable("maze_basement", "SCENE", scene, "mg_props.maze_basement"),
                    DriverVariable("stairs", "OBJECT", obj_cells, f'modifiers["{names.stairs}"].strength'),
                ],
                expression="maze_basement and stairs != 0",
            ),
        )

        setup_mod2mod_driver(obj_cells, names.subdiv, "levels", obj_cells, names.subdiv, show, "var > 0")

    setup_driver_from_addon_props(obj_cells, names.wireframe, "material_offset", scene, "cell_props.cell_contour_black")
    setup_driver_from_addon_props(
        obj_cells, names.bevel, "miter_outer", scene, "cell_props.cell_contour_black", "2 if var else 0"
    )
    setup_driver_from_addon_props(
        obj_cells, names.bevel, "miter_inner", scene, "cell_props.cell_contour_black", "2 if var else 0"
    )
    setup_driver_from_addon_props(
        obj_cells, names.bevel, "profile", scene, "cell_props.cell_contour_black", "1 if var else 0.5"
    )
    setup_driver_from_addon_props(
        obj_cells, names.bevel, "material", scene, "cell_props.cell_contour_black", "1 if var else 0"
    )
    setup_driver_from_addon_props(
        obj_cells, names.bevel, "segments", scene, "cell_props.cell_contour_black", "2 if var else 4"
    )
    setup_driver_from_addon_props(
        obj_cells, names.decimate, "ratio", scene, "cell_props.cell_decimate", "1 - var / 100"
    )

    setup_mod2mod_driver(obj_cells, names.subdiv, "levels", obj_cells, names.subdiv, "render_levels")
    setup_mod2mod_driver(
        obj_cells, names.mask_longest_path, "show_viewport", obj_cells, names.mask_longest_path, "show_render"
    )
