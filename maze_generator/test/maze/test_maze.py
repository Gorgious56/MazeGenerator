import unittest
from maze_generator.maze_v2 import algorithm, maze, graph


class TestMaze(unittest.TestCase):
    def setUp(self):
        self.rows = 5
        self.columns = self.rows
        _graph = graph.new_grid(self.columns, self.rows)
        self.maze = maze.new(_graph, algorithm.Algorithm(graph=_graph))

    def tearDown(self):
        self.maze = None

    def test_creating_a_maze(self):
        self.assertIsInstance(self.maze, maze.Maze)

    def test_that_a_grid_algo_is_correctly_associated_with_a_graph_and_an_algorithm(self):
        self.assertIn("algorithm", self.maze.__dict__)
        self.assertIsNotNone(self.maze.algorithm)
        self.assertIn("graph", self.maze.__dict__)
        self.assertIsNotNone(self.maze.graph)

    def test_running_a_maze_algorithm(self):
        self.maze.algorithm.run()

    def test_that_all_cells_can_be_reached_after_running_the_algorithm(self):
        self.maze.algorithm.run()
        previous_cell = (0, 0)
        for x in range(self.columns):
            for y in range(self.rows):
                if x == y == 0:
                    continue
                self.assertTrue(self.maze.graph.are_reachable(previous_cell, (x, y)))
                previous_cell = (x, y)
