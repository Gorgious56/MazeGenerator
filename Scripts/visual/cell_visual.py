DISTANCE = 'DISTANCE'
GROUP = 'GROUP'
UNIFORM = 'UNIFORM'
NEIGHBORS = 'NEIGHBORS'

DEFAULT_CELL_VISUAL_TYPE = DISTANCE


def generate_cell_visual_enum():
    return [(DISTANCE, 'Distance', ''),
            (GROUP, 'Cell Group', ''),
            (UNIFORM, 'Uniform', ''),
            (NEIGHBORS, 'Neighbors Amount', ''),
            ]


DISPLACE = 'DISPLACE'

VERTEX_GROUPS = DISPLACE, 


class CellVisual:
    def __init__(self, cell):
        self.cell = cell

        self.faces = []
        self.walls = []

        self.color_layers = {}

    def __str__(self):
        ret = 'Cell Visual(r' + str(self.cell.row) + ';c' + str(self.cell.column) + ')'
        ret += '\n faces: ' + str(len(self.faces))
        return ret

    def __repr__(self):
        return self.__str__()

    def create_wall(self, wall_a, wall_b):
        self.walls.append(wall_a)
        self.walls.append(wall_b)

    def add_face(self, vertices, vertices_levels=None):
        if vertices_levels is None:
            vertices_levels = [0 for i in range(len(vertices))]
        f = CellVisual.Face()
        [f.add_vertex(v, v_level) for v, v_level in zip(vertices, vertices_levels)]
        self.faces.append(f)

    def get_faces_with_vertex_weights(self):
        return [f for f in self.faces if f.vertex_groups is not None]    

    class Face:
        def __init__(self):
            self.vertices = []
            self.vertices_indexes = []
            self.vertices_levels = []
            self.edges = []
            self.face = None
            self.vertex_groups = None

        def corners(self):
            return len(self.vertices)

        def add_vertex(self, vec, level):
            self.vertices.append(vec)
            self.vertices_levels.append(level)

        def add_edges(self, delta):
            self.edges = [(delta + i, delta + ((i + 1) % self.corners())) for i in range(self.corners())]

        def add_face(self, delta):
            self.face = [delta + i for i in range(len(self.edges))]

        def translate(self, delta):
            self.add_edges(delta)
            self.add_face(delta)
            self.vertices_indexes = [i + delta for i in range(len(self.vertices))]

        def set_vertex_group(self, vertex_group_name, weights):
            if self.vertex_groups:
                self.vertex_groups[vertex_group_name] = weights
            else:
                self.vertex_groups = {vertex_group_name: weights}
