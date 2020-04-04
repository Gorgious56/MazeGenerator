WALL_WELD_NAME = 'MG_WELD'
WALL_SCREW_NAME = 'MG_SCREW'
WALL_SOLIDIFY_NAME = 'MG_SOLIDIFY'
WALL_BEVEL_NAME = 'MG_BEVEL'

CELL_WELD_NAME = 'MG_WELD'
CELL_WELD_2_NAME = 'MG_WELD_2'
CELL_SOLIDIFY_NAME = 'MG_SOLIDIFY'
CELL_DECIMATE_NAME = 'MG_DECIMATE'
CELL_SUBSURF_NAME = 'MG_SUBSURF'
CELL_BEVEL_NAME = 'MG_CONTOUR'
CELL_WIREFRAME_NAME = 'MG_WIREFRAME'
CELL_DISPLACE_NAME = 'MG_DISPLACE'
CELL_CYLINDER_NAME = 'MG_CYLINDER'
CELL_WELD_CYLINDER_NAME = 'MG_CYLINDER_WELD'
CELL_MOEBIUS_NAME = 'MG_MOEBIUS'
CELL_TORUS_NAME = 'MG_TORUS'
CELL_STAIRS_NAME = 'MG_STAIRS'


def add_modifier(obj, mod_type, mod_name, remove_if_already_exists=False, remove_all_modifiers=False, properties=None, overwrite_props=True):
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
                    setattr(mod, prop, value)


def add_driver_to(obj, obj_prop, var_name, id_type, id, prop_path, expression=None):
    if obj:
        driver = obj.driver_add(obj_prop).driver
        try:
            var = driver.variables[0]
        except IndexError:
            var = driver.variables.new()
        var.name = var_name
        var.type = 'SINGLE_PROP'

        target = var.targets[0]
        target.id_type = id_type
        target.id = id
        target.data_path = prop_path

        if expression:
            driver.expression = expression
        else:
            driver.expression = var_name
