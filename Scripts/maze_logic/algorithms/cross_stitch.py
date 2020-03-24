from . maze_algorithm import MazeAlgorithm


class CrossStitch(MazeAlgorithm):
    def __init__(self, grid, _seed, _max_steps=-1, bias=0):
        super().__init__(_seed=_seed, _max_steps=_max_steps, bias=bias)

        self.expeditions = 1

        self.unvisited_legit_cells = []

        direction = -1
        self.current = None

        self.set_current(grid.random_cell(_seed))

        self.current.group = 1

        while self.current and not self.must_break():
            unvisited_neighbor, direction = self.current.get_biased_unmasked_unlinked_directional_neighbor(bias, direction)

            if unvisited_neighbor:
                self.link_to(self.current, unvisited_neighbor)
                self.set_current(unvisited_neighbor)
            else:
                self.set_current(None)
            self.next_step()

            while self.unvisited_legit_cells:
                c = self.unvisited_legit_cells[0]
                if self.must_break():
                    break
                if not c.has_any_link():
                    neighbor = c.get_biased_unmasked_linked_neighbor(bias, 5)
                    if neighbor:
                        self.set_current(c)
                        self.link_to(self.current, neighbor)
                        self.next_step()

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
        other_c.group = self.expeditions + 2
        self.next_step()

    def set_current(self, c):
        self.current = c
        if c:
            c.group = self.expeditions
            unvisited_neighbors = self.current.get_unlinked_neighbors()
            self.add_to_unvisited_legit_cells(unvisited_neighbors)
        else:
            self.direction = - 1

    def add_to_unvisited_legit_cells(self, cells):
        self.unvisited_legit_cells.extend([c for c in cells if c not in self.unvisited_legit_cells])
