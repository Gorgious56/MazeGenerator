"""
Methods to store, acces and create drivers
"""


from collections.abc import Iterable


def setup_driver_from_addon_props(obj, mod_name, obj_to_prop, scene, addon_prop, expression=None):
    setup_driver(
        obj.modifiers[mod_name],
        DriverProperties(obj_to_prop, DriverVariable('var', 'SCENE', scene, f"mg_props.{addon_prop}"),
                         expression))


class DriverProperties:
    """
    Stores driver properties used when setting up drivers
    """

    def __init__(self, prop_to, variables, expression=None, prop_to_dim=-1):
        self.prop = prop_to
        self.prop_dim = prop_to_dim
        if not isinstance(variables, Iterable):
            self.variables = (variables,)
            self.expression = expression if expression else variables.name
        else:
            self.variables = variables
            self.expression = expression if expression else variables[0].name


class DriverVariable:
    """
    Stores Variables used in a driver
    """

    def __init__(self, name, id_type, _id, data_path):
        self.name = name
        self.id_type = id_type
        self.id = _id
        self.data_path = data_path


def copy_mod2mod_driver(obj_from, mod, mod_prop, obj_to, expression=None):
    setup_mod2mod_driver(obj_from, mod, mod_prop, obj_to,
                         mod, mod_prop, expression)


def setup_mod2mod_driver(
        obj_from,
        mod_from,
        mod_prop_from,
        obj_to,
        mod_to,
        mod_prop_to,
        expression=None):
    setup_driver(
        obj_to.modifiers[mod_to],
        DriverProperties(
            mod_prop_to,
            DriverVariable('var', 'OBJECT', obj_from,
                           f'modifiers["{mod_from}"].{mod_prop_from}'),
            expression=expression))


def setup_driver(obj, drv_props: DriverProperties):
    if not obj:
        return

    if drv_props.prop_dim >= 0:
        drivers = (obj.driver_add(drv_props.prop, drv_props.prop_dim),)
    else:
        drivers = obj.driver_add(drv_props.prop)
        if not isinstance(drivers, list):
            drivers = (drivers,)

    for drv in drivers:
        drv = drv.driver
        for i, var_props in enumerate(drv_props.variables):
            if i < len(drv.variables):
                var = drv.variables[i]
            else:
                var = drv.variables.new()
            var.name = var_props.name
            var.type = 'SINGLE_PROP'

            target = var.targets[0]
            target.id_type = var_props.id_type
            target.id = var_props.id
            target.data_path = str(var_props.data_path)

        drv.expression = drv_props.expression
