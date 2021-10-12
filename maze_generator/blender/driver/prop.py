from collections.abc import Iterable


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
