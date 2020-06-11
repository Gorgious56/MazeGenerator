from bpy.utils import register_class, unregister_class
from .import auto_load
from .operators import op_generate_maze, op_tweak_maze_size, op_sample_mazes
from .visual import ui_panel, gizmos

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

classes = (
    op_generate_maze.GenerateMazeOperator,
    op_generate_maze.RefreshMazeOperator,
    op_tweak_maze_size.TweakMazeSizeOperator,
    op_sample_mazes.SampleMazesOperator,
    ui_panel.MazeGeneratorPanel,
    ui_panel.ParametersPanel,
    ui_panel.CellsPanel,
    ui_panel.WallsPanel,
    ui_panel.DisplayPanel,
    ui_panel.InfoPanel,
    gizmos.MazeWidgetGroup,
    )


def register():
    auto_load.register()
    for cls in classes:
        register_class(cls)


def unregister():
    auto_load.unregister()
    for cls in reversed(classes):
        unregister_class(cls)
