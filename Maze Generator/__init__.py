"""
Main file required by Blender Add-on
"""
from bpy.utils import register_class, unregister_class
from . import auto_load
from .panels.main import MazeGeneratorPanel

bl_info = {
    "name": "Maze Generator",
    "author": "Nathan Hild",
    "description": "Add-on for generating mazes with a bunch of settings",
    "blender": (2, 83, 0),
    "version": (0, 4, 0),
    "location": "",
    "warning": "",
    "category": "Add Mesh",
    "doc_url": "https://github.com/Gorgious56/MazeGenerator/blob/master/README.md",
}

al = auto_load.AutoLoad()


def register():
    register_class(MazeGeneratorPanel)
    al.register()

def unregister():
    al.unregister()
