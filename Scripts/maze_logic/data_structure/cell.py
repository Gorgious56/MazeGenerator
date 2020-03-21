class Cell:
    neighbors_return = [2, 3, 0, 1]

    def __init__(self, row, col):
        self.row = row
        self.column = col

        self.group = 0

        self.neighbors = [None] * 4
        # 0>North - 1>West - 2>South - 3>East

        self.links = {}

        self.is_masked = False

    def __str__(self):
        return 'Cell(r' + str(self.row) + ';c' + str(self.column) + ')'

    def __repr__(self):
        return self.__str__()

    def link(self, other_cell, bidirectional=True):
        self.links[other_cell] = True
        if bidirectional:
            other_cell.link(self, False)

    def unlink(self, other_cell, bidirectional=True):
        try:
            del self.links[other_cell]
        except KeyError:
            pass
        if bidirectional:
            other_cell.unlink(self, False)

    def is_linked(self, other_cell):
        return other_cell in self.links

    def has_any_link(self):
        return any(self.links)

    def get_neighbors(self):
        return [n for n in self.neighbors if n]

    def get_unlinked_neighbors(self):
        return [c for c in self.get_neighbors() if not c.has_any_link()]

    def get_linked_neighbors(self):
        return [c for c in self.get_neighbors() if c.has_any_link()]

    def exists_and_is_linked(self, other_cell):
        return other_cell is not None and self.is_linked(other_cell)

    def exists_and_is_linked_neighbor_index(self, neighbor_index):
        return self.exists_and_is_linked(self.neighbors[neighbor_index])

    def get_wall_mask(self):
        return [not self.exists_and_is_linked(n) for n in self.neighbors] if self.has_any_link() else [False] * len(self.neighbors)
