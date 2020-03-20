def add_modifier(obj, mod_type, mod_name, remove_if_already_exists=False, remove_all_modifiers=False, properties=None):
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
        if mod and type(properties) is dict:
            for prop, value in properties.items():
                if hasattr(mod, prop):
                    setattr(mod, prop, value)
