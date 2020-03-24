from random import choices
from . maze_algorithm import MazeAlgorithm
from .. data_structure . cell_polar import CellPolar
from .. data_structure . cell import Cell
from .. data_structure . cell_triangle import CellTriangle
from .. data_structure . cell_hex import CellHex


class BinaryTree(MazeAlgorithm):
    def __init__(self, grid, _seed, _max_steps=-1, bias=0):
        super().__init__(_seed=_seed, _max_steps=_max_steps, bias=bias)
        expeditions = 1

        for c in grid.each_cell():
            if self.must_break():
                break
            c_type = type(c)
            if c_type is CellTriangle:
                if c.is_upright():
                    if c.row == grid.rows - 1 and c.neighbors[0]:
                        neighbors = [c.neighbors[0]]
                    else:
                        neighbors = [n for n in c.neighbors[0:2] if n]
                else:
                    if c.row == grid.rows - 1 and c.neighbors[1]:
                        neighbors = [c.neighbors[1]]
                    else:
                        neighbors = [n for n in [c.neighbors[2]] if n]
            elif c_type is Cell:
                neighbors = [n for n in c.neighbors[0:2] if n]
            elif c_type is CellHex:
                if c.row == grid.rows - 1:
                    neighbors = [n for n in [c.neighbors[5 if c.column % 2 == 0 else 0]] if n]
                else:
                    neighbors = [n for n in c.neighbors[0:3] if n]
            elif c_type is CellPolar:
                neighbors = c.outward
                this_row = grid.rows_polar[c.row]

                linked_to_outer_ring = False
                if c.column == len(this_row) - 1:
                    for other_c in this_row:
                        for n in other_c.outward:
                            if other_c.is_linked(n):
                                linked_to_outer_ring = True
                                break
                if linked_to_outer_ring or c.column != len(this_row) - 1:
                    direction = c.ccw if _seed % 2 == 0 else c.cw
                    if direction:
                        neighbors.append(direction)

            link = c.get_biased_choice(neighbors, bias, 5)
            if link:
                c.link(link)
                link.group = expeditions + 1
                if c.group == 0:
                    c.group = expeditions

            self.next_step()
