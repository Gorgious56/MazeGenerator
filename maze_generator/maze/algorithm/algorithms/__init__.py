"""
Algorithm manager methods and properties
"""

from maze_generator.maze.cell.constants import CellType
from maze_generator.maze.space_representation.constants import SpaceRepresentation

# Algorithms :
from .maze_algorithm import MazeAlgorithm

from .binary_tree import BinaryTree
from .sidewinder import Sidewinder
from .cross_stitch import CrossStitch
from .eller import Eller
from .prim import Prim
from .wilson import Wilson
from .growing_tree import GrowingTree
from .hunt_and_kill import HuntAndKill
from .recursive_backtracker import RecursiveBacktracker
from .aldous_broder import AldousBroder
from .aldous_broder_copy import AldousBroderCopy
from .recursive_division import RecursiveDivision
from .recursive_voronoi_division import RecursiveVoronoiDivision
from .voronoi_division import VoronoiDivision
from .kruskal_random import KruskalRandom


def work(grid, props):
    try:
        algorithm_class_from_name(props.algorithm.algorithm)(grid, props)
        # ALGORITHM_FROM_NAME[props.algorithm.algorithm](grid, props)
    except KeyError:
        pass


def all_algorithm_classes():
    return MazeAlgorithm.__subclasses__()


def all_algorithms_names():
    return [alg_class.name for alg_class in all_algorithm_classes()]


def algorithm_class_from_name(alg_name):
    for alg in all_algorithm_classes():
        if alg.name == alg_name:
            return alg
    return None


DEFAULT_ALGO = RecursiveBacktracker.name

WEAVED_ALGORITHMS = [algo.name for algo in all_algorithm_classes() if algo.weaved]


def is_algo_incompatible(props):
    if (
        algorithm_class_from_name(props.algorithm.algorithm) == AldousBroder
        and props.space_rep_props.representation == SpaceRepresentation.BOX.value
    ):
        return "Aldous-Broder can't solve a box representation"
    if props.space_rep_props.representation == SpaceRepresentation.BOX.value and props.maze_weave:
        return "Can't solve weaved maze for a box"
    if algorithm_class_from_name(props.algorithm.algorithm) in (RecursiveDivision, VoronoiDivision) and props.cell_props.is_a(
        CellType.POLAR
    ):
        return "Can't solve this algorithm with Polar grid (yet)"
    return False


def is_algo_weaved(props):
    return props.cell_props.is_a(CellType.SQUARE) and props.algorithm.algorithm in WEAVED_ALGORITHMS


def is_kruskal_random(algo_name):
    return algo_name == KruskalRandom.name


def generate_algo_enum():
    return [(alg_name, alg_name, "") for alg_name in all_algorithms_names()]
