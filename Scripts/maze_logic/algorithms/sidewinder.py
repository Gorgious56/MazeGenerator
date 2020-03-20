from random import choice, randint
from . maze_algorithm import MazeAlgorithm


class Sidewinder(MazeAlgorithm):
    def __init__(self, grid, _seed, _max_steps=-1, close_chance=1):
        super().__init__(_seed=_seed, _max_steps=_max_steps)

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
                if (c.neighbors[3] is None) or (c.neighbors[0] is not None and randint(0, close_chance) < 1):
                    member = choice(run)
                    if member.neighbors[0]:
                        member.link(member.neighbors[0])
                        member.neighbors[0].group = 2
                    run = []
                else:
                    c.link(c.neighbors[3])
                self.next_step()
