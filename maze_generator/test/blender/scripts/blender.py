import bpy
from maze_generator.maze_v2 import mesh, maze, obj


def purge():
    bpy.data.batch_remove(bpy.data.objects)
    bpy.data.batch_remove(bpy.data.meshes)


def test_creating_a_maze_mesh_where_cells_are_connected_by_edges():
    _maze = maze.new_grid(columns=10, rows=10)
    _maze.algorithm.run(seed=0)
    mesh_maze = mesh.MazeMesh(maze=_maze)
    mesh_maze.create_a_mesh_where_cells_are_connected_by_edges()
    _mesh = mesh_maze.mesh
    assert len(_mesh.vertices) == len(_maze.graph.nodes)
    assert len(_mesh.edges) == len(_maze.graph.links)


def test_creating_a_mesh_where_edges_define_walls():
    _maze = maze.new_grid(columns=10, rows=10)
    _maze.algorithm.run(seed=0)
    mesh_maze = mesh.MazeMesh(maze=_maze)
    mesh_maze.create_a_mesh_where_edges_define_walls()
    _mesh = mesh_maze.mesh
    walls = len(_maze.graph.connections_with_no_link)
    assert len(_mesh.vertices) == 2 * (walls + 2 * _maze.rows + 2 * _maze.columns)
    assert len(_mesh.edges) == walls + 2 * _maze.rows + 2 * _maze.columns


def test_creating_a_mesh_where_points_with_rotation_attribute_define_walls():
    _maze = maze.new_grid(columns=10, rows=10)
    _maze.algorithm.run(seed=0)
    mesh_maze = mesh.MazeMesh(maze=_maze)
    mesh_maze.create_a_mesh_where_points_with_rotation_attribute_define_walls()
    _mesh = mesh_maze.mesh
    walls = len(_maze.graph.connections_with_no_link)
    assert len(_mesh.vertices) == walls + 2 * _maze.rows + 2 * _maze.columns
    assert len(_mesh.edges) == 0
    assert "rotation" in _mesh.attributes


def test_creating_an_obj_with_geometry_nodes():
    _maze = maze.new_grid(columns=10, rows=10)
    _maze.algorithm.run(seed=0)
    mesh_maze = mesh.MazeMesh(maze=_maze)
    mesh_maze.create_a_mesh_where_points_with_rotation_attribute_define_walls()
    obj_maze = obj.MazeObject(mesh_maze.mesh, bpy.context.collection)


if __name__ == "__main__":
    test_creating_a_maze_mesh_where_cells_are_connected_by_edges()
    purge()
    test_creating_a_mesh_where_edges_define_walls()
    purge()
    test_creating_a_mesh_where_points_with_rotation_attribute_define_walls()
    purge()
    test_creating_an_obj_with_geometry_nodes()
    purge()
