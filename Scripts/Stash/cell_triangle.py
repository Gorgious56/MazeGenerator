import cell

class CellTriangle(cell.Cell):
    neighbors_return = [0, 2, 1]

    def __init__(self, row, col):
        super().__init__(row, col)
        self.neighbors = [None] * 3
        self.neighbors_name = ["North East", "North West", "South"] if self.is_upright() else ["South West", "South East", "North"]
        # self.neighbors_name = [str(self)]*3

    def is_upright(self):
        return (self.row + self.column) % 2 == 1

    