from random import choice
from random import seed
from random import randint


class Sidewinder:
    def __init__(self, grid, _seed, _max_steps=-1, close_chance=1):
        steps = 100000 if _max_steps < 0 else _max_steps
        seed(_seed)
        for row in grid.each_row():
            if steps < 0:
                break
            run = []
            for c in row:
                if c.group == 0:
                    c.group = 1
                if steps < 0:
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
                steps -= 1
