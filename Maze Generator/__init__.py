import sys
import inspect
from bpy.utils import register_class, unregister_class
from . import auto_load
from .visual import ui_panel, gizmos
from .operators import op_sample_mazes, op_generate_maze, op_tweak_maze_size

bl_info = {
    "name": "Maze Generator",
    "author": "Nathan Hild",
    "description": "Add-on for generating mazes with a bunch of settings",
    "blender": (2, 83, 0),
    "version": (0, 3, 0),
    "location": "",
    "warning": "",
    "category": "Add Mesh",
    "doc_url": "https://github.com/Gorgious56/MazeGenerator/blob/master/README.md",
}

auto_load.init()

classes = []


def batch_add_classes(module, sort_by=None, sort_reverse=False):
    new_classes = inspect.getmembers(sys.modules[module.__name__], lambda member: inspect.isclass(member) and member.__module__ == module.__name__)
    if sort_by:
        new_classes.sort(key=sort_by, reverse=sort_reverse)
    classes.extend([cl[1] for cl in new_classes])


batch_add_classes(module=ui_panel, sort_by=lambda cl: cl[1].order)
batch_add_classes(module=op_generate_maze)
batch_add_classes(module=op_tweak_maze_size)
batch_add_classes(module=op_sample_mazes)
batch_add_classes(module=gizmos)


def register():
    auto_load.register()
    for cls in classes:
        register_class(cls)


def unregister():
    auto_load.unregister()
    for cls in reversed(classes):
        unregister_class(cls)
