"""
Base Maze Algorithm Class
Inherit from this class to extend or create a custom algorithm
"""

from random import (
    seed,
    random,
    shuffle,
)
from maze_generator.module.constants import grid_logic as cst


class MazeAlgorithm(object):
    """
    Base Maze Algorithm Class
    Inherit from this class to extend or create a custom algorithm
    """

    name = __name__
    weaved = True
    settings = ["bias", "maze_weave"]

    def __init__(self, grid=None, props=None):
        self.grid = grid
        self.bias = props.algorithm.bias
        self._seed = props.algorithm.seed
        seed(self._seed)

    def add_template_passages(self):
        grid = self.grid
        if hasattr(grid, "weave"):
            potential_passages = []
            for c in range(1, grid.columns - 1):
                for r in range(1, grid.rows - 1):
                    potential_passages.append(grid[c, r])
            shuffle(potential_passages)

            for pp in potential_passages[0 : round(grid.weave * len(potential_passages))]:
                self.add_crossing(pp)

    def color_cells_by_tree_root(self):
        union_find = self.grid._union_find
        links = []
        for c in self.grid.all_cells:
            link = union_find.find(c)
            if link:
                try:
                    c.group = links.index(link)
                except ValueError:
                    links.append(link)
                    c.group = len(links) - 1

    def add_crossing(self, cell):
        grid = self.grid
        can_cross = not cell.has_any_link()
        if can_cross:
            north = cell.neighbor(cst.NORTH)
            west = cell.neighbor(cst.WEST)
            south = cell.neighbor(cst.SOUTH)
            east = cell.neighbor(cst.EAST)
            if random() > 0.5:  # Vertical underway
                grid.link(cell, west)
                grid.link(cell, east)

                new_cell_under = self.grid.tunnel_under(cell)

                grid.link(north, north.neighbor(cell.get_neighbor_return(cst.NORTH)))
                grid.link(south, south.neighbor(cell.get_neighbor_return(cst.SOUTH)))
            else:
                grid.link(cell, north)
                grid.link(cell, south)

                new_cell_under = self.grid.tunnel_under(cell)

                grid.link(west, west.neighbor(cell.get_neighbor_return(cst.WEST)))
                grid.link(east, east.neighbor(cell.get_neighbor_return(cst.EAST)))
            return True
        return False
