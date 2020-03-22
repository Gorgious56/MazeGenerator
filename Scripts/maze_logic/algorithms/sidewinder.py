from random import choice, randint
from . maze_algorithm import MazeAlgorithm
from .. data_structure . cell_polar import CellPolar
from .. data_structure . cell import Cell
from .. data_structure . cell_triangle import CellTriangle
from .. data_structure . cell_hex import CellHex


class Sidewinder(MazeAlgorithm):
    def __init__(self, grid, _seed, _max_steps=-1, bias=0):
        super().__init__(_seed=_seed, _max_steps=_max_steps, bias=bias)

        for row in grid.each_row():
            if self.must_break():
                break
            run = []
            for c in row:
                if c.group == 0:
                    c.group = 1
                if self.must_break():
                    break
                run.append(c)

                c_type = type(c)
                if c_type is Cell:
                    if (c.neighbors[3] is None) or (c.neighbors[0] and randint(0, self.parameter) < 1):
                        member = choice(run)
                        if member.neighbors[0]:
                            member.link(member.neighbors[0])
                            member.neighbors[0].group = 2
                        run = []
                    else:
                        c.link(c.neighbors[3])
                elif c_type is CellTriangle:
                    if c.is_upright():
                        if c.neighbors[0]:
                            c.link(c.neighbors[0])
                        else:
                            if len(run) == 1:
                                c.link(c.neighbors[1])
                            else:
                                member = choice([c for c in run if not c.is_upright()])
                                if member.neighbors[2]:
                                    member.link(member.neighbors[2])
                                    member.neighbors[2].group = 4
                            run = []
                        if c.row == grid.rows - 1 and c.neighbors[1]:
                            c.link(c.neighbors[1])
                    else:
                        if (c.neighbors[1] is None) or (c.neighbors[1] is not None and randint(0, close_chance) < 1):
                            member = choice([c for c in run if not c.is_upright()])
                            if member.neighbors[2]:
                                member.link(member.neighbors[2])
                                member.neighbors[2].group = 4
                            run = []
                        else:
                            c.link(c.neighbors[1])
                elif c_type is CellHex:
                    other = 5 if c.column % 2 == 0 else 0
                    # if c.column % 2 == 0:
                    if (c.neighbors[other] is None) or (c.neighbors[other] and randint(0, self.parameter) < 1):
                        member = choice(run)
                        north_neighbors = [n for n in c.neighbors[0:3] if n and not n.has_any_link()]
                        if north_neighbors:
                            linked_neighbor = choice(north_neighbors)
                            member.link(linked_neighbor)
                            linked_neighbor.group = 2
                        elif c.neighbors[5]:
                            c.link(c.neighbors[other])
                        run = []
                    else:
                        c.link(c.neighbors[other])
                    # else:
                    #     if (c.neighbors[0] is None) or (c.neighbors[0] and randint(0, close_chance) < 1):
                    #         member = choice(run)
                    #         north_neighbors = [n for n in c.neighbors[0:3] if n]
                    #         if north_neighbors:
                    #             linked_neighbor = choice(north_neighbors)
                    #             member.link(linked_neighbor)
                    #             linked_neighbor.group = 2
                    #         elif c.neighbors[0]:
                    #             c.link(c.neighbors[0])
                    #         run = []
                    #     else:
                    #         c.link(c.neighbors[0])
                self.next_step()
