"""
Variation to the Sidewinder

Strong diagonal texture from the central point.
"""


from .maze_algorithm import (
    MazeAlgorithm,
    get_biased_choices,
)


class CrossStitch(MazeAlgorithm):
    """
    Variation to the Sidewinder

    Strong diagonal texture from the central point.
    """

    name = "Cross-Stitch"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.expeditions = 1
        self.unvisited_legit_cells = []
        self.current = None

        self.run()

    def run(self):
        grid = self.grid
        _seed = self._seed
        direction = -1
        self.set_current(grid.random_cell(_seed))

        self.current.group = 1

        while self.current:
            unvisited_neighbor, direction = self.current.get_biased_unlinked_directional_neighbor(self.bias, direction)

            if unvisited_neighbor:
                self.link_to(self.current, unvisited_neighbor)
                self.set_current(unvisited_neighbor)
            else:
                self.set_current(None)

            while self.unvisited_legit_cells:
                c = self.unvisited_legit_cells[0]
                if not c.has_any_link():
                    neighbor = get_biased_choices(c.get_linked_neighbors(), self.bias)[0]
                    if neighbor:
                        self.set_current(c)
                        self.link_to(self.current, neighbor)

    def link_to(self, c, other_c):
        self.grid.link(c, other_c)
        if other_c in self.unvisited_legit_cells:
            self.unvisited_legit_cells.remove(other_c)
        if c in self.unvisited_legit_cells:
            self.unvisited_legit_cells.remove(c)
        other_c.group = self.expeditions + 2

    def set_current(self, c):
        self.current = c
        if c:
            c.group = self.expeditions
            unvisited_neighbors = self.current.get_unlinked_neighbors()
            self.add_to_unvisited_legit_cells(unvisited_neighbors)
        else:
            self.direction = -1

    def add_to_unvisited_legit_cells(self, visited_cells):
        self.unvisited_legit_cells.extend([c for c in visited_cells if c not in self.unvisited_legit_cells])
