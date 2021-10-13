from maze_generator.blender.info.ui.panel import InfoPanel
from maze_generator.blender.object.walls.ui.panel import WallsPanel
from maze_generator.blender.generation.ui.panel import MazeGeneratorPanel
from maze_generator.blender.object.cells.ui.panel import CellsPanel
from maze_generator.maze.grid.ui.panel import ParametersPanel
from maze_generator.maze.pathfinding.ui.panel import PathPanel
from maze_generator.maze.algorithm.ui.panel import AlgorithmPanel
from maze_generator.maze.space_representation.ui.panel import SpaceRepresentationPanel

panels = (
    MazeGeneratorPanel,
    AlgorithmPanel,
    ParametersPanel,
    SpaceRepresentationPanel,
    CellsPanel,
    WallsPanel,
    PathPanel,
    InfoPanel,
)
