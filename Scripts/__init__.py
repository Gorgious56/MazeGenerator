from bpy . utils import register_class, unregister_class
from . import auto_load
from . visual import ui_panel

bl_info = {
    "name": "Maze Generator",
    "author": "Nathan Hild",
    "description": "Add-on for generating mazes with a bunch of settings",
    "blender": (2, 80, 3),
    "version": (0, 0, 2),
    "location": "",
    "warning": "",
    "category": "Add Mesh"
}

auto_load.init()

classes = ui_panel.MazeGeneratorPanel, ui_panel.ParametersPanel, ui_panel.CellsPanel, ui_panel.WallsPanel, ui_panel.DisplayPanel, ui_panel.InfoPanel


def register():
    auto_load.register()
    for cls in classes:
        register_class(cls)


def unregister():
    auto_load.unregister()
    for cls in classes:
        unregister_class(cls)
