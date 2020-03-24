from . cell import Cell


class CellPolar(Cell):

    def __init__(self, row, column):
        super().__init__(row, column)
        self.cw = None
        self.ccw = None
        self.inward = None
        self.outward = []

    def get_neighbors(self):
        neighbors = []
        for n in [self.cw, self.ccw, self.inward]:
            if n:
                neighbors.append(n)
        neighbors.extend(self.outward)
        return neighbors

    def get_wall_mask(self):
        return [not self.exists_and_is_linked(n) for n in self.neighbors] if self.has_any_link() else [False] * len(self.neighbors)

    def is_linked_outward(self):
        is_linked_outward = False
        for n in self.outward:
            if n and self.is_linked(n):
                is_linked_outward = True
                break
        return is_linked_outward

    def has_outward_neighbor(self):
        return len(self.outward) > 0
