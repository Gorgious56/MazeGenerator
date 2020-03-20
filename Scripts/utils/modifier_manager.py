def add_modifier(obj, mod_type, mod_name, remove_if_already_exists=False, remove_all_modifiers=False):
    mod_name = mod_name if mod_name != "" else "Fallback"

    if obj is not None:
        if remove_all_modifiers:
            obj.modifiers.clear()

        if mod_name in obj.modifiers:
            if remove_if_already_exists:
                obj.modifiers.remove(obj.modifiers.get(mod_name))
                add_modifier()
        else:
            obj.modifiers.new(mod_name, mod_type)
