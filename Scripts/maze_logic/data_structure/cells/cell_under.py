from .cell import Cell


class CellUnder(Cell):
    def __init__(self, cell_over):
        super().__init__(cell_over.row, cell_over.column)        
        neighbors = (0, 2) if cell_over.is_horizontal_passage() else (1, 3)
        for n in neighbors:
            self.neighbors[n] = cell_over.neighbors[n]
            cell_over.neighbors[n].neighbors[self.get_neighbor_return(n)] = self
            self.link(self.neighbors[n])

    def is_horizontal_passage(self):
        return self.neighbors[1] or self.neighbors[3]

    def is_vertical_passage(self):
        return self.neighbors[0] or self.neighbors[2]

    def is_passage_in_direction(self, direction):
        return self.is_horizontal_passage() if direction % 2 == 0 else self.is_vertical_passage()
