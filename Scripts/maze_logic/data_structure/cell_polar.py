from . cell import Cell


class CellPolar(Cell):
    def __init__(self, row, column):
        super().__init__(row, column)
        self.neighbors = [None, None, None, []]
        # 0>cw - 1>ccw - 2>inward - 3>outward

    def get_neighbors(self):
        neighbors_ret = []
        for n in self.neighbors:
            if n:
                if n is list:
                    neighbors_ret.extend(n)
                else:
                    neighbors_ret.append(n)
        return neighbors_ret
