from .maze_algorithm import MazeAlgorithm
from ..helper.random import get_biased_choices


class KruskalRandom(MazeAlgorithm):
    name = "Kruskal Randomized"
    settings = ["bias", "maze_weave"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_template_passages()

        self.run()
        self.color_cells_by_tree_root()

    def run(self):
        grid = self.grid
        unvisited_cells = grid.shuffled_cells()
        for c in unvisited_cells:
            for n in get_biased_choices(c.neighbors, self.bias, k=len(c.neighbors)):
                if not grid.connected(c, n):
                    grid.link(c, n)  # Keep this because of the weave maze
