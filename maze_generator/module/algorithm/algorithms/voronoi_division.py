from random import shuffle, randrange
from math import hypot
from .maze_algorithm import MazeAlgorithm
from maze_generator.helper.union_find import UnionFind


class VoronoiDivision(MazeAlgorithm):
    name = "Voronoi Division"
    settings = ["room_size"]

    def __init__(self, grid, props=None, *args, **kwargs):
        super().__init__(grid=grid, props=props, *args, **kwargs)

        self.room_size = props.algorithm.room_size
        self.room_size_deviation = props.algorithm.room_size_deviation
        self.rooms = grid.size // self.room_size

        all_cells = self.grid.all_cells.copy()

        shuffle(all_cells)
        self.union_find = UnionFind(all_cells)

        self.room_centers = all_cells[0 : self.rooms]

        self.expeditions = 0

        # Destroy all walls:
        [[grid.link(c, n, False) for n in c.neighbors if n.level == c.level] for c in all_cells]
        self.run(all_cells)

    def run(self, cells):
        union_find = self.union_find

        frontiers = []
        [frontiers.append({}) for room in range(self.rooms)]

        for c in self.grid.all_cells:
            dmin = 100000000
            j = -1
            for i, r_c in enumerate(self.room_centers):
                d = hypot(r_c.column - c.column, r_c.row - c.row)
                if d < dmin:
                    dmin = d
                    j = i
            if j >= 0:
                union_find.union(c, self.room_centers[j])
                c.group = j

        cell_centers_union_groups = [union_find.find(c) for c in self.room_centers]

        for c in self.grid.all_cells:
            for n in [n for n in c.neighbors if not union_find.connected(c, n)]:
                try:
                    frontiers[cell_centers_union_groups.index(union_find.find(c))][
                        cell_centers_union_groups.index(union_find.find(n))
                    ].append((c, n))
                except KeyError:
                    frontiers[cell_centers_union_groups.index(union_find.find(c))][
                        cell_centers_union_groups.index(union_find.find(n))
                    ] = [(c, n)]

        linked_cells = []
        for frontier_dic in frontiers:
            for ind, frontier in frontier_dic.items():
                already_open = False
                for lc in linked_cells:
                    if lc in frontier:
                        linked_cells.remove(lc)
                        already_open = True
                if frontier and not already_open:
                    actual_psg = frontier[randrange(0, len(frontier))]
                    if not union_find.connected(actual_psg[0], actual_psg[1]):
                        frontier.remove(actual_psg)
                        union_find.union(actual_psg[0], actual_psg[1])
                        linked_cells.append((actual_psg[1], actual_psg[0]))
                    for link in [link for link in frontier if len(link[0].links) > 1 and len(link[1].links) > 1]:
                        link[0].unlink(link[1])
