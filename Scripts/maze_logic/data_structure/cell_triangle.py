from . cell import Cell


class CellTriangle(Cell):
    neighbors_return = [0, 2, 1]

    def __init__(self, row, col):
        super().__init__(row, col)
        self.neighbors = [None] * 3

    def is_upright(self):
        return (self.row + self.column) % 2 == 1
