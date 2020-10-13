"""
Simple algorithm

A strong vertical texture.
Mandatory corridor along the Top of the maze
"""


from random import random, shuffle
from .maze_algorithm import MazeAlgorithm


class Sidewinder(MazeAlgorithm):
    """
    Simple algorithm

    A strong vertical texture.
    Mandatory corridor along the Top of the maze
    """
    name = 'Sidewinder'
    weaved = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bias = (self.bias + 1) / 2

        self.run()
        self.color_cells_by_tree_root()

    def run(self):
        grid = self.grid
        for row in grid.each_row():
            run = []
            for c in row:
                run.append(c)
                east_neighbor = grid.delta_cell(c, column=1)
                link_north = False
                if not east_neighbor or \
                    c.column == grid.get_columns_this_row(c.row) - 1 or \
                    (grid.delta_cell(c, row=1) and self.must_close_run()):
                    shuffle(run)
                    for member in run:
                        next_row = grid.delta_cell(member, row=1)
                        if next_row and next_row in member.neighbors:
                            grid.link(member, next_row)
                            run = []
                            link_north = True
                            break
                if not link_north:
                    if east_neighbor:
                        grid.link(c, east_neighbor)
                    else:
                        grid.link(c, grid.delta_cell(c, column=-1))

    def must_close_run(self):
        return self.bias > random()
