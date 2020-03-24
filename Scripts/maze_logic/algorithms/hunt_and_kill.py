from random import choice
from . maze_algorithm import MazeAlgorithm


class HuntAndKill(MazeAlgorithm):
    def __init__(self, grid, _seed, _max_steps=-1, bias=0):
        super().__init__(_seed=_seed, _max_steps=_max_steps, bias=bias)
        self.grid = grid

        self.unvisited_legit_cells = []

        self.expeditions = 2

        self.direction = - 1

        self.on()

    def on(self):

        self.unvisited_legit_cells = []
        if self.must_break():
            return
        self.set_current(self.grid.random_cell(self._seed))

        self.add_to_unvisited_legit_cells(self.current.get_unlinked_neighbors())

        while self.current and not self.must_break():
            while self.current and not self.must_break():
                neighbor, self.direction = self.current.get_biased_unmasked_unlinked_directional_neighbor(self.bias, self.direction)
                if neighbor:
                    self.link_to(self.current, neighbor)
                    self.set_current(neighbor)
                    if self.must_break():
                        break
                else:
                    self.current = None
            if self.must_break():
                break
            try:
                self.expeditions += 1
                self.set_current(choice(self.unvisited_legit_cells))
                neighbor = choice(self.current.get_linked_neighbors())
                self.link_to(neighbor, self.current)

                self.direction = neighbor.get_direction(self.current)

                self.add_to_unvisited_legit_cells(self.current.get_unlinked_neighbors())
            except IndexError:  # Neighbors is empty
                break

    def link_to(self, c, other_c):
        c.link(other_c)
        try:
            self.unvisited_legit_cells.remove(other_c)
        except ValueError:
            pass
        try:
            self.unvisited_legit_cells.remove(c)
        except ValueError:
            pass
        other_c.group = self.expeditions
        self.next_step()

    def set_current(self, c):
        self.current = c
        c.group = self.expeditions
        unvisited_neighbors = self.current.get_unlinked_neighbors()
        self.add_to_unvisited_legit_cells(unvisited_neighbors)

    def add_to_unvisited_legit_cells(self, cells):
        self.unvisited_legit_cells.extend([c for c in cells if c not in self.unvisited_legit_cells])