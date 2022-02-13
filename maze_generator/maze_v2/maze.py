from math import sqrt
from maze_generator.maze_v2 import graph, algorithm


class Maze:
    def __init__(self, graph, algorithm) -> None:
        self.graph = graph
        self.algorithm = algorithm

    def __repr__(self):
        cells = len(self.graph.nodes)
        rows = columns = int(sqrt(cells))
        ret = self.__class__.__name__
        ret += "\n"
        for y in range(rows * 2, -1, -1):
            for x in range(columns * 2 + 1):
                if x == 0 or y == 0 or x == columns * 2 or y == rows * 2:
                    ret += "*"
                elif y % 2 == 1 and x % 2 == 1:
                    ret += " "
                elif x % 2 == 0 and y % 2 == 0:
                    ret += "*"
                elif x % 2 == 0:
                    left_cell = (int((x - 2) / 2), int((y - 1) / 2))
                    right_cell = (left_cell[0] + 1, left_cell[1])
                    if self.graph.linked(left_cell, right_cell):
                        print(right_cell, left_cell)
                        ret += " "
                    else:
                        ret += "*"
                else:
                    bottom_cell = (int((x - 1) / 2), int((y - 2) / 2))
                    top_cell = (bottom_cell[0], bottom_cell[1] + 1)
                    if self.graph.linked(bottom_cell, top_cell):
                        ret += " "
                    else:
                        ret += "*"
            ret += "\n"
        return ret


class MazeGrid(Maze):
    def __init__(self, rows, columns, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.rows = rows
        self.columns = columns


def new(graph, algorithm):
    return Maze(graph, algorithm)


def new_grid(columns=10, rows=10):
    my_graph = graph.new_grid(columns, rows)
    my_algorithm = algorithm.Algorithm(my_graph)
    return MazeGrid(rows, columns, my_graph, my_algorithm)
