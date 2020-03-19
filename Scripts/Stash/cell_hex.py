import cell

class CellHex(cell.Cell):
    neighbors_return = [3, 4, 5, 0, 1, 2]
    neighbors_name = ["North East", "North", "North West", "South West", "South", "South East"]

    def __init__(self, row, col):
        super().__init__(row, col)
        self.neighbors = [None] * 6