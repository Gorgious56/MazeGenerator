from . import auto_load

bl_info = {
    "name": "Maze Generator",
    "author": "NH",
    "description": "",
    "blender": (2, 80, 0),
    "version":  (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Generic"
}

auto_load.init()


def register():
    auto_load.register()


def unregister():
    auto_load.unregister()
