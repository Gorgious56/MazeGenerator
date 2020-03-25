from . cell import Cell


class CellOver(Cell):
    def __init__(self, grid, *args, **kwards):
        super().__init__(*args, **kwards)
        self.neighbors_over = None
        self.grid = grid

    def get_neighbors(self):
        if self.neighbors_over is None:
            self.neighbors_over = [None] * len(self.neighbors_return)
            for i, neighbor in enumerate(self.neighbors):
                self.neighbors_over[i] = neighbor.neighbors[i] if self.can_tunnel_towards(i) else None
        ns = super().get_neighbors()
        ns.extend([n for n in self.neighbors_over if n])
        return ns

    def can_tunnel_towards(self, direction):
        direction_neighbor = self.neighbors[direction]
        return direction_neighbor and direction_neighbor.neighbors[direction] and direction_neighbor.is_passage_in_direction(direction)

    def is_passage_in_direction(self, direction):
        return self.is_horizontal_passage() if direction % 2 == 0 else self.is_vertical_passage()

    def is_horizontal_passage(self):
        return self.is_linked(self.neighbors[1]) and self.is_linked(self.neighbors[3]) and not self.is_linked(self.neighbors[0]) and not self.is_linked(self.neighbors[2])

    def is_vertical_passage(self):
        return not self.is_linked(self.neighbors[1]) and not self.is_linked(self.neighbors[3]) and self.is_linked(self.neighbors[0]) and self.is_linked(self.neighbors[2])

    def link(self, other_cell, bidirectional=True):
        neighbor_passage = None
        for i, neighbor in enumerate(self.neighbors):
            if neighbor and neighbor == other_cell.neighbors[self.get_neighbor_return(i)]:
                neighbor_passage = neighbor
                break
        if neighbor_passage:
            self.grid.tunnel_under(neighbor_passage)
        else:
            super().link(other_cell, bidirectional=bidirectional)
