from . binary_tree import BinaryTree
from . sidewinder import Sidewinder
from . cross_stitch import CrossStitch
from . aldous_broder import AldousBroder
from . wilson import Wilson
from . hunt_and_kill import HuntAndKill
from . recursive_backtracker import RecursiveBacktracker

DEFAULT_ALGO = 'ALGO_RECURSIVE_BACKTRACKER'

ALGO_BINARY_TREE = 'ALGO_BINARY_TREE'
ALGO_SIDEWINDER = 'ALGO_SIDEWINDER'
ALGO_CROSS_STITCH = 'ALGO_CROSS_STITCH'
ALGO_ALDOUS_BRODER = 'ALGO_ALDOUS_BRODER'
ALGO_WILSON = 'ALGO_WILSON'
ALGO_HUNT_AND_KILL = 'ALGO_HUNT_AND_KILL'
ALGO_RECURSIVE_BACKTRACKER = 'ALGO_RECURSIVE_BACKTRACKER'


def generate_algo_enum():
    return [(ALGO_BINARY_TREE, 'Binary Tree', ''),
            (ALGO_SIDEWINDER, 'Sidewinder', ''),
            (ALGO_CROSS_STITCH, 'Cross Stitch', ''),
            (ALGO_ALDOUS_BRODER, 'Aldous-Broder', ''),
            (ALGO_WILSON, 'Wilson', ''),
            (ALGO_HUNT_AND_KILL, 'Hunt And Kill', ''),
            (ALGO_RECURSIVE_BACKTRACKER, 'Recursive Backtracker', ''),
            ]


def work(algorithm, grid, seed, max_steps=-1):
    if algorithm == ALGO_BINARY_TREE:
        BinaryTree(grid, seed, max_steps)
    if algorithm == ALGO_SIDEWINDER:
        Sidewinder(grid, seed, max_steps)
    if algorithm == ALGO_CROSS_STITCH:
        CrossStitch(grid, seed, max_steps)
    if algorithm == ALGO_ALDOUS_BRODER:
        AldousBroder(grid, seed, max_steps)
    if algorithm == ALGO_WILSON:
        Wilson(grid, seed, max_steps)
    if algorithm == ALGO_HUNT_AND_KILL:
        HuntAndKill(grid, seed, max_steps)
    if algorithm == ALGO_RECURSIVE_BACKTRACKER:
        RecursiveBacktracker(grid, seed, max_steps)
