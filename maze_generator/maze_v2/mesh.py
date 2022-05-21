import bpy
from mathutils import Vector


class MazeMesh:
    def __init__(self, maze) -> None:
        self.maze = maze
        self.mesh = None

    def create_mesh(self):
        self.mesh = bpy.data.meshes.new("mesh")

    def init_mesh(self, verts, edges=None, faces=None):
        if edges is None:
            edges = ()
        if faces is None:
            faces = ()
        if self.mesh is None:
            self.create_mesh()
        self.mesh.clear_geometry()
        self.mesh.from_pydata(verts, edges, faces)

    def create_a_mesh_where_cells_are_connected_by_edges(self) -> None:
        graph = self.maze.graph
        nodes = list(graph.nodes)
        verts = [(v[0], v[1], 0) for v in nodes]
        edges = [(nodes.index(n1), nodes.index(n2)) for (n1, n2) in graph.links]
        self.init_mesh(verts=verts, edges=edges)

    def create_a_mesh_where_edges_define_walls(self) -> None:
        verts = []
        edges = []
        graph = self.maze.graph
        connections_with_no_link = list(graph.connections_with_no_link)
        for node_1, node_2 in connections_with_no_link:
            if node_1[1] == node_2[1]:  # Vertical Wall
                x = float((node_1[0] + node_2[0]) / 2)
                y = node_1[1]
                verts.append((x, y - 0.5, 0.0))
                verts.append((x, y + 0.5, 0.0))
                edges.append((len(verts) - 1, len(verts) - 2))
            else:  # Horizontal Wall
                x = node_1[0]
                y = float((node_1[1] + node_2[1]) / 2)
                verts.append((x - 0.5, y, 0.0))
                verts.append((x + 0.5, y, 0.0))
                edges.append((len(verts) - 1, len(verts) - 2))
        for node in graph.nodes:
            if node[0] == 0:
                verts.append((-0.5, node[1] - 0.5, 0.0))
                verts.append((-0.5, node[1] + 0.5, 0.0))
                edges.append((len(verts) - 1, len(verts) - 2))
            if node[0] == self.maze.columns - 1:
                verts.append((self.maze.columns - 0.5, node[1] - 0.5, 0.0))
                verts.append((self.maze.columns - 0.5, node[1] + 0.5, 0.0))
                edges.append((len(verts) - 1, len(verts) - 2))
            if node[1] == 0:
                verts.append((node[0] - 0.5, -0.5, 0.0))
                verts.append((node[0] + 0.5, -0.5, 0.0))
                edges.append((len(verts) - 1, len(verts) - 2))
            if node[1] == self.maze.rows - 1:
                verts.append((node[0] - 0.5, self.maze.rows - 0.5, 0.0))
                verts.append((node[0] + 0.5, self.maze.rows - 0.5, 0.0))
                edges.append((len(verts) - 1, len(verts) - 2))

        self.init_mesh(verts=verts, edges=edges)

    def create_a_mesh_where_points_with_rotation_attribute_define_walls(self) -> None:
        verts = []
        graph = self.maze.graph
        connections_with_no_link = list(graph.connections_with_no_link)
        states = []  # list where 0 = horizontal, 1 = vertical

        for node_1, node_2 in connections_with_no_link:
            if node_1[1] == node_2[1]:  # Vertical Wall
                x = float((node_1[0] + node_2[0]) / 2)
                y = node_1[1]
                verts.append((x, y, 0.0))
                states.append(False)
            else:  # Horizontal Wall
                x = node_1[0]
                y = float((node_1[1] + node_2[1]) / 2)
                verts.append((x, y, 0.0))
                states.append(True)
        for node in graph.nodes:
            if node[0] == 0:
                verts.append((-0.5, node[1], 0.0))
                states.append(False)
            if node[0] == self.maze.columns - 1:
                verts.append((self.maze.columns - 0.5, node[1], 0.0))
                states.append(False)
            if node[1] == 0:
                verts.append((node[0], -0.5, 0.0))
                states.append(True)
            if node[1] == self.maze.rows - 1:
                verts.append((node[0], self.maze.rows - 0.5, 0.0))
                states.append(True)

        self.init_mesh(verts=verts)

        def get_flattened_vec():
            for s in states:
                yield from (0, 0, s * 3.14 / 2)

        states = list(get_flattened_vec())

        self.mesh.attributes.new("rotation", "FLOAT_VECTOR", "POINT")
        attribute = self.mesh.attributes.active
        attribute.data.foreach_set("vector", states)
