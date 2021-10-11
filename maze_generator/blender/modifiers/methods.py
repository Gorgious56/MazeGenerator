"""
Methods to store, access or create modifiers
"""


from typing import Dict
import bpy.types as bpy_types


class ModifierCreator:
    """
    Helper class t ocreate modifiers
    """

    def __init__(self, _type: str, name: str, properties: Dict, _object: bpy_types.Object = None):
        self.object = _object
        self.type = _type
        self.name = name
        self.properties = properties

    def set_property(self, name, value):
        self.properties[name] = value


def add_modifier(
    creator: ModifierCreator,
    remove_if_already_exists: bool = False,
    remove_all_modifiers: bool = False,
    overwrite_props: bool = True,
) -> None:

    mod_name = creator.name if creator.name != "" else "Fallback"
    obj = creator.object

    if not obj:
        return
    mod = None
    if remove_all_modifiers:
        obj.modifiers.clear()

    if mod_name in obj.modifiers:
        if remove_if_already_exists:
            obj.modifiers.remove(obj.modifiers.get(mod_name))
            add_modifier(creator, remove_if_already_exists, remove_all_modifiers)
        else:
            mod = obj.modifiers.get(mod_name)
    else:
        mod = obj.modifiers.new(mod_name, creator.type)

    # Setting modifier properties
    if not mod or not overwrite_props:
        return
    for prop, value in creator.properties.items():
        if hasattr(mod, prop):
            setattr(mod, prop, value)
