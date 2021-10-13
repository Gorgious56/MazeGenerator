"""
Manager module for object modifiers
"""

from maze_generator.blender.object.cells import modifiers as cells_mods
from maze_generator.blender.object.walls import modifiers as walls_mods


def setup_modifiers(scene, props, preferences) -> None:
    cells_mods.setup_modifiers(scene, props, preferences)
    walls_mods.setup_modifiers(scene, props, preferences)
