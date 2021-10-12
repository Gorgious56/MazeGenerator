"""
Main file required by Blender Add-on
"""
from bpy.utils import register_class, unregister_class
from maze_generator import auto_load
from maze_generator.blender.ui.panels import panels


bl_info = {
    "name": "Maze Generator",
    "author": "Gorgious",
    "description": "Add-on for generating mazes with a bunch of settings",
    "blender": (2, 83, 0),
    "version": (0, 4, 1),
    "location": "",
    "warning": "",
    "category": "Add Mesh",
    "doc_url": "https://github.com/Gorgious56/MazeGenerator/blob/master/README.md",
}


def register():
    for panel in panels:
        register_class(panel)
    auto_load.init()
    auto_load.register()


def unregister():
    auto_load.unregister()
    for panel in reversed(panels):
        unregister_class(panel)
