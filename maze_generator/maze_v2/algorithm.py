import random


class Algorithm:
    def __init__(self, graph=None) -> None:
        self.cell_current = None
        if graph:
            self.set_graph(graph)
        else:
            self.graph = None
            self.cell_total_count = None

    def set_graph(self, graph):
        self.graph = graph
        self.cell_total_count = len(list(graph.nodes_with_at_least_one_neighbor))

    def run(self, seed=None):
        self.set_seed(seed)
        self.cell_current = (0, 0)
        unvisited = self.cell_total_count - 1
        while unvisited > 0:
            neighbor = random.choice(list(self.graph.get_neighbors(self.cell_current)))
            if not self.graph.is_linked(neighbor):
                self.graph.link(self.cell_current, neighbor)
                unvisited -= 1
            self.cell_current = neighbor

    def set_seed(self, seed):
        if seed is not None:
            random.seed(seed)
