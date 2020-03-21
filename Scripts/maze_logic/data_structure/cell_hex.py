from . cell import Cell


class CellHex(Cell):
    neighbors_return = [3, 4, 5, 0, 1, 2]

    def __init__(self, row, col):
        super().__init__(row, col)
        self.neighbors = [None] * 6
