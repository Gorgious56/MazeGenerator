from random import choice
from random import seed


class BinaryTree:
    def __init__(self, grid, _seed, _max_steps=-1):
        steps = 100000 if _max_steps < 0 else _max_steps
        seed(_seed)

        expeditions = 1

        for c in grid.each_cell():
            if steps <= 0:
                break
            neighbors = [n for n in c.neighbors[0: 1 + len(c.neighbors) // 2] if n]

            if len(neighbors) > 0:
                link = choice(neighbors)
                c.link(link)
                link.group = expeditions + 1
                if c.group == 0:
                    c.group = expeditions
            steps -= 1
