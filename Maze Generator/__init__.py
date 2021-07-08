"""
Main file required by Blender Add-on
"""
from bpy.utils import register_class, unregister_class
from . import auto_load
from .ui.panels.main import MazeGeneratorPanel

bl_info = {
    "name": "Maze Generator",
    "author": "Gorgious",
    "description": "Add-on for generating mazes with a bunch of settings",
    "blender": (2, 83, 0),
    "version": (0, 4, 0),
    "location": "",
    "warning": "",
    "category": "Add Mesh",
    "doc_url": "https://github.com/Gorgious56/MazeGenerator/blob/master/README.md",
}

def register():
    register_class(MazeGeneratorPanel)
    auto_load.init()
    auto_load.register()


def unregister():
    auto_load.unregister()
    unregister_class(MazeGeneratorPanel)
