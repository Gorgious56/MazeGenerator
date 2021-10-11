from maze_generator.module.cell.ui.panel import CellsPanel
from maze_generator.module.grid.ui.panel import ParametersPanel
from maze_generator.module.display.ui.panel import DisplayPanel
from maze_generator.module.pathfinding.ui.panel import PathPanel
from maze_generator.module.wall.ui.panel import WallsPanel
from maze_generator.module.info.ui.panel import InfoPanel
from maze_generator.module.algorithm.ui.panel import AlgorithmPanel
from maze_generator.module.space_representation.ui.panel import SpaceRepresentationPanel
from maze_generator.module.generation.ui.panel import MazeGeneratorPanel

panels = (
    MazeGeneratorPanel,
    AlgorithmPanel,
    ParametersPanel,
    SpaceRepresentationPanel,
    CellsPanel,
    WallsPanel,
    DisplayPanel,
    PathPanel,
    InfoPanel,
)
