"""
Simple algorithm

No particular texture.
Generates a lot of dead-ends.
"""


from math import ceil
from random import random, randrange, choices
from .maze_algorithm import MazeAlgorithm


class Eller(MazeAlgorithm):
    """
    Simple algorithm

    No particular texture.
    Generates a lot of dead-ends.
    """
    name = 'Eller'
    weaved = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bias = (self.bias + 1) / 2

        self.run()

        self.color_cells_by_tree_root()

    def run(self):
        grid = self.grid
        for row in grid.each_row():
            sets_this_row = {}
            for c in row:
                next_col = grid.delta_cell(c, column=1)
                if next_col and \
                    ((c.row == grid.rows - 1 or self.bias < random()) and \
                    not grid.connected(c, next_col)):
                    grid.link(c, next_col)
            for c in row:
                this_set = grid.find(c)
                if this_set in sets_this_row:
                    sets_this_row[this_set].append(c)
                else:
                    sets_this_row[this_set] = [c]

            for tree, cells in sets_this_row.items():
                ch_len = min(len(cells), randrange(1, ceil(self.bias * len(cells) + 2)))
                for c in choices(cells, k=ch_len):
                    neigh = grid.delta_cell(c, row=1)
                    if neigh not in c.neighbors:
                        other_col = grid.delta_cell(c, column=1)
                        if not other_col:
                            other_col = grid.delta_cell(c, column=-1)
                        grid.link(other_col, grid.delta_cell(other_col, row=1))
                        neigh = other_col
                    if neigh:
                        grid.link(c, neigh)
