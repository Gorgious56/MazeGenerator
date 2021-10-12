from math import hypot
from .maze_algorithm import (
    MazeAlgorithm,
    randrange,
    UnionFind,
)


class RecursiveVoronoiDivision(MazeAlgorithm):
    name = "Recursive Voronoi Division"
    settings = ["room_size", "room_size_deviation"]

    def __init__(self, grid, props=None, *args, **kwargs):
        super().__init__(grid=grid, props=props, *args, **kwargs)

        self.room_size = props.algorithm.room_size
        self.room_size_deviation = props.algorithm.room_size_deviation

        self.expeditions = 0

        all_cells = self.grid.all_cells.copy()

        # Destroy all walls:
        [[grid.link(c, n, False) for n in c.neighbors if n.level == c.level] for c in all_cells]
        self.run(all_cells)

    def run(self, cells):
        # Interpretation of https://rosettacode.org/wiki/Voronoi_diagram#Python with two points
        # Could use actual sets for the data at the cost of determinism
        if len(cells) <= max(
            2, randrange(int(self.room_size * (1 - (self.room_size_deviation / 100))), self.room_size + 1)
        ):
            return

        # Choose two cells at random
        c_a, c_b = cells.pop(randrange(0, len(cells))), cells.pop(randrange(0, len(cells)))

        set_a, set_b, frontier = [c_a], [c_b], []

        # Build the voronoi diagram : Each set will contain the cell if it is closest to one of the randomly chosen point
        # There is a slight bias toward set_b but the calculation save is worth it
        [
            (
                set_a
                if hypot(c.column - c_a.column, c.row - c_a.row) < hypot(c.column - c_b.column, c.row - c_b.row)
                else set_b
            ).append(c)
            for c in cells
        ]

        # Add the frontier walls to a container
        [
            [frontier.append((c_set_a, c_set_b)) for c_set_b in [_n for _n in c_set_a.neighbors if _n in set_b]]
            for c_set_a in set_a
        ]

        union_find_a = UnionFind(set_a)
        union_find_b = UnionFind(set_a)

        for c in set_a:
            c.group = self.expeditions
            for n in [n for n in c.neighbors if n in set_a]:
                union_find_a.union(c, n)
        for c in set_b:
            c.group = self.expeditions
            for n in [n for n in c.neighbors if n in set_b]:
                union_find_b.union(c, n)
        self.expeditions += 1

        # Unlink all the cells in the frontier but one
        if len(frontier) > 0:
            actual_psg = frontier.pop(randrange(0, len(frontier)))
            self.grid.link(actual_psg[0], actual_psg[1])
            for psg in frontier:
                # Make sure we don't close dead-ends or cells which got isolated from their set
                if (
                    len(psg[0].links) > 1
                    and len(psg[1].links) > 1
                    and union_find_a.connected(psg[0], c_a)
                    and union_find_b.connected(psg[1], c_b)
                ):
                    psg[0].unlink(psg[1])
            [self.run(s_x) for s_x in (set_a, set_b)]
