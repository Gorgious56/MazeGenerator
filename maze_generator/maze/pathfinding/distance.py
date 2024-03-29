"""
This module handles distance calculations inside the maze
"""


class Distances:
    """
    This class handles distance calculations inside the maze
    """

    def __init__(self, root):
        self.root = root
        self.cells = {}
        self.cells[root] = 1
        self.path = []
        self.max_distance = 0
        self.get_distances()

    def __delitem__(self, key):
        del self.cells[key]

    def __getitem__(self, key):
        return self.cells.get(key, None)

    def __setitem__(self, key, value):
        self.cells[key] = value

    @property
    def all_cells(self):
        return self.cells.keys()

    def get_distances(self):
        frontier = [self.root]
        while len(frontier) > 0:
            new_frontier = []

            for c in [_c for _c in frontier if _c]:
                for link in c.links:
                    if self[link] is None:
                        self[link] = self[c] + 1
                        new_frontier.append(link)
            frontier = new_frontier

        return self.cells

    def path_to(self, goal):
        current = goal

        breadcrumbs = Distances(self.root)
        breadcrumbs.path = [current]
        breadcrumbs[current] = self[current]

        while current != self.root and current.has_any_link():
            for link in current.links:
                if self[link] < self[current]:
                    breadcrumbs[link] = self[link]
                    current = link
                    breadcrumbs.path.append(link)
                    break
        breadcrumbs.path.reverse()
        return breadcrumbs

    @property
    def max(self):
        self.max_distance = 0
        max_cell = self.root

        for c, d in self.cells.items():
            if d > self.max_distance:
                max_cell = c
                self.max_distance = d
        return max_cell, self.max_distance

    def reverse(self):
        for c, d in self.cells.items():
            self[c] = max(1, self.max_distance - d)
