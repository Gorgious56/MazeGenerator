from random import choice
from .maze_algorithm import MazeAlgorithm


class HuntAndKill(MazeAlgorithm):
    name = "Hunt And Kill"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unvisited_legit_cells = []
        self.expeditions = 2
        self.direction = -1

        self.run()

    def run(self):
        self.set_current(self.grid.random_cell(self._seed))

        self.add_to_unvisited_legit_cells(self.current.get_unlinked_neighbors())

        while self.current:
            while self.current:
                neighbor, self.direction = self.current.get_biased_unlinked_directional_neighbor(
                    self.bias, self.direction
                )
                if neighbor:
                    self.link_to(self.current, neighbor)
                    self.set_current(neighbor)
                else:
                    self.current = None
            try:
                self.expeditions += 1
                self.set_current(choice(self.unvisited_legit_cells))
                neighbor = choice(self.current.get_linked_neighbors())
                self.link_to(neighbor, self.current)

                self.direction = neighbor.get_neighbor_direction(self.current)

                self.add_to_unvisited_legit_cells(self.current.get_unlinked_neighbors())
            except IndexError:  # Neighbors is empty
                break

    def link_to(self, c, other_c):
        self.grid.link(c, other_c)
        if other_c in self.unvisited_legit_cells:
            self.unvisited_legit_cells.remove(other_c)
        if c in self.unvisited_legit_cells:
            self.unvisited_legit_cells.remove(c)

        other_c.group = self.expeditions

    def set_current(self, c):
        self.current = c
        c.group = self.expeditions
        unvisited_neighbors = self.current.get_unlinked_neighbors()
        self.add_to_unvisited_legit_cells(unvisited_neighbors)

    def add_to_unvisited_legit_cells(self, visited_cells):
        self.unvisited_legit_cells.extend([c for c in visited_cells if c not in self.unvisited_legit_cells])
