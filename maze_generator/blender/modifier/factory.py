from maze_generator.blender.modifier.tool import ensure_modifier


def ensure_solidify_mod(obj):
    mod = ensure_modifier(obj, "MG_MOD_SOLIDIFY", "SOLIDIFY")
    mod.solidify_mode = "NON_MANIFOLD"
    mod.offset = 0
    mod.thickness = 0.1  # TODO Addonprefs
    return mod
