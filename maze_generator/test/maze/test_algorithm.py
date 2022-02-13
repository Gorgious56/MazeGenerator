import unittest
from maze_generator.maze_v2 import algorithm, graph


class TestAlgorithm(unittest.TestCase):
    def setUp(self):
        self.algo = algorithm.Algorithm()

    def tearDown(self):
        self.algo = None


class TestAlgorithmCreation(TestAlgorithm):
    def test_creating_an_algorithm(self):
        self.assertIsInstance(self.algo, algorithm.Algorithm)

    def test_that_a_new_algorithm_has_a_current_cell_attribute(self):
        self.assertIn("cell_current", self.algo.__dict__)


class TestAlgorithmLogic(TestAlgorithm):
    def test_using_the_same_seed_yields_the_same_result(self):
        for value in (5, 8):
            graph_a = graph.new_grid(value, value)
            self.algo.set_graph(graph_a)
            self.algo.run(seed=value)
            graph_b = graph.new_grid(value, value)
            self.algo.set_graph(graph_b)
            self.algo.run(seed=value)
            self.assertEqual(graph_a, graph_b)
