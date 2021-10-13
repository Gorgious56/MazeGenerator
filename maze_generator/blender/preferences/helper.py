from maze_generator.blender.preferences.constants import addon_name

def get_preferences(context):
    return context.preferences.addons[addon_name].preferences
