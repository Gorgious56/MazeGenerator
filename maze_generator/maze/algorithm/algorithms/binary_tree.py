"""
One of the most simple algorithms

A strong diagonal texture.
Mandatory corridors along the Top and Right of the maze
"""


from .maze_algorithm import (
    MazeAlgorithm,
    get_biased_choices,
)


class BinaryTree(MazeAlgorithm):
    """
    One of the most simple algorithms

    A strong diagonal texture.
    Mandatory corridors along the Top and Right of the maze
    """

    name = "Binary Tree"
    weaved = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run()
        self.color_cells_by_tree_root()

    def run(self):
        grid = self.grid
        bias = self.bias
        for c in grid.all_cells:
            neighbors = []
            east_neighbor = grid.delta_cell(c, column=1)
            columns_this_row = grid.get_columns_this_row(c.row)
            if east_neighbor and east_neighbor in c.neighbors and c.column < columns_this_row - 1:
                neighbors.append(east_neighbor)
            if not east_neighbor or c.row < grid.rows - 1:
                next_row = grid.delta_cell(c, row=1)
                if next_row in c.neighbors:
                    neighbors.append(next_row)
                elif c.column == columns_this_row - 1:
                    prev_column = grid.delta_cell(c, column=-1)
                    if prev_column:
                        grid.link(c, prev_column)
                        c = prev_column
                        neighbors = [grid.delta_cell(c, row=1)]
            if grid.levels > 1 and c.row == self.grid.rows - 1:
                next_level = grid.delta_cell(c, level=1)
                if next_level in c.neighbors:
                    neighbors.append(next_level)
            if not neighbors:
                continue
            link_neighbor = get_biased_choices(neighbors, bias, 5)[0]
            if not grid.connected(c, link_neighbor):
                grid.link(c, link_neighbor)
