"""
Manager module for object modifiers
"""

from maze_generator.blender.object.cells import modifiers as cells_mods
from maze_generator.blender.object.walls import modifiers as walls_mods


def setup_modifiers(scene, props) -> None:
    cells_mods.setup_modifiers(scene, props)
    walls_mods.setup_modifiers(scene, props)
