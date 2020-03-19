from random import choice, seed


class HuntAndKill:
    def __init__(self, grid, _seed=-1, _max_steps=-1):
        self.grid = grid

        self.unvisited_legit_cells = []

        self.steps = 100000 if _max_steps < 0 else _max_steps

        self._seed = _seed
        seed(_seed)

        self.expeditions = 2

        self.on()

    def on(self):

        self.initialize()
        while self.current and self.steps > 0:
            while self.current and self.steps > 0:
                unvisited_neighbors = self.current.get_unlinked_neighbors()
                try:
                    neighbor = choice(unvisited_neighbors)
                    self.link_to(self.current, neighbor)
                    unvisited_neighbors.remove(neighbor)
                    self.add_to_unvisited_legit_cells(unvisited_neighbors)
                    self.set_current(neighbor)
                    if self.steps <= 0:
                        break
                except IndexError:  # unvisited_neighbors is empty
                    self.current = None
            if self.steps <= 0:
                break
            try:
                self.expeditions += 1
                self.set_current(choice(self.unvisited_legit_cells)) 
                neighbor = choice(self.current.get_linked_neighbors())
                self.link_to(neighbor, self.current)                                

                self.add_to_unvisited_legit_cells(self.current.get_unlinked_neighbors())
            except IndexError:  # Neighbors is empty
                break

    def initialize(self):
        self.unvisited_legit_cells = []

        self.steps -= 1
        if self.steps < 0:
            return
        self.set_current(self.grid.random_cell(self._seed))

        self.add_to_unvisited_legit_cells(self.current.get_unlinked_neighbors())

    def link_to(self, c, other_c):
        c.link(other_c)
        try:
            self.unvisited_legit_cells.remove(other_c)
        except ValueError:
            pass
        other_c.group = self.expeditions
        self.steps -= 1

    def set_current(self, c):
        self.current = c
        c.group = self.expeditions

    def add_to_unvisited_legit_cells(self, cells):
        self.unvisited_legit_cells.extend([c for c in cells if c not in self.unvisited_legit_cells])

#        for c in cells:
#            c.group = 1