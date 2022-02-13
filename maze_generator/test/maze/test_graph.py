import unittest
from maze_generator.maze_v2 import graph


class TestGraph(unittest.TestCase):
    def setUp(self):
        self.graph = graph.new()

    def tearDown(self):
        self.graph = None

    def test_creating_a_graph(self):
        self.assertIsInstance(self.graph, graph.OrderedGraph)


class TestGraphGrid(unittest.TestCase):
    def setUp(self):
        self.rows = 5
        self.columns = self.rows
        self.size = self.rows * self.columns
        self.graph = graph.new_grid(columns=self.columns, rows=self.rows)

    def tearDown(self):
        self.graph = None

    def test_creating_a_graph_decribing_a_grid(self):
        self.assertIsInstance(self.graph, graph.OrderedGraph)
        self.assertEqual(self.size, len(self.graph.nodes))
        for x in range(self.columns):
            for y in range(self.rows):
                if x < self.columns - 1:
                    self.assertTrue(self.graph.connected((x, y), (x + 1, y)))
                if y < self.rows - 1:
                    self.assertTrue(self.graph.connected((x, y), (x, y + 1)))

    def test_that_all_cells_in_a_grid_cell_have_at_least_one_neighbor(self):
        self.assertEqual(len(self.graph.nodes), len(list(self.graph.nodes_with_at_least_one_neighbor)))
