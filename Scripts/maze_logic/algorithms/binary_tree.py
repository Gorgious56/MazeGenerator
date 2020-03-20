from random import choice
from . maze_algorithm import MazeAlgorithm


class BinaryTree(MazeAlgorithm):
    def __init__(self, grid, _seed, _max_steps=-1, close_chance=1):
        super().__init__(_seed=_seed, _max_steps=_max_steps)
        expeditions = 1

        for c in grid.each_cell():
            if self.must_break():
                break
            neighbors = [n for n in c.neighbors[0:2] if n]

            if len(neighbors) > 0:
                link = choice(neighbors)
                c.link(link)
                link.group = expeditions + 1
                if c.group == 0:
                    c.group = expeditions
            self.next_step()
