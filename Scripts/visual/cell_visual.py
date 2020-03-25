from mathutils import Vector


class Face:
    def __init__(self, connection):
        self.vertices = []
        self.edges = []
        self.face = None
        self.connection = connection

    def corners(self):
        return len(self.vertices)

    def add_vertex(self, vec):
        self.vertices.append(vec)

    def add_edges(self, delta):
        self.edges = [(delta + i, delta + ((i + 1) % self.corners())) for i in range(self.corners())]

    def add_face(self, delta):
        self.face = [delta + i for i in range(len(self.edges))]

    def translate(self, delta):
        self.add_edges(delta)
        self.add_face(delta)


class CellVisual:
    def __init__(self, cell, positions):
        self.cell = cell

        self.p = positions

        self.faces = []
        self.walls = []

        self.color_layers = {}

    def __str__(self):
        ret = 'Cell Visual(r' + str(self.cell.row) + ';c' + str(self.cell.column) + ')'
        ret += '\n faces: ' + str(len(self.faces))
        return ret

    def __repr__(self):
        return self.__str__()

    def create_wall(self, wall_a_x, wall_a_y, wall_b_x, wall_b_y):
        p = self.p
        self.walls.append(Vector([p[wall_a_x], p[wall_a_y], 0]))
        self.walls.append(Vector([p[wall_b_x], p[wall_b_y], 0]))

    def add_face(self, vertices_x, vertices_y, connection=False):
        f = Face(connection)
        [f.add_vertex(Vector([self.p[vtb_x], self.p[vtb_y], 0])) for vtb_x, vtb_y in zip(vertices_x, vertices_y)]
        self.faces.append(f)
