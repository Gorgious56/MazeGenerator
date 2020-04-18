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


VG_DISPLACE, VG_STAIRS, VG_THICKNESS = 'MG_DISPLACE', 'MG_STAIRS', 'MG_CELL_THICKNESS'

VERTEX_GROUPS = VG_DISPLACE, VG_STAIRS, VG_THICKNESS


class CellVisual:
    def __init__(self, cell):
        self.cell = cell

        self.faces = []

        self.vertex_groups = None

        self.color_layers = {}

    def __str__(self):
        ret = 'Cell Visual(r' + str(self.cell.row) + ';c' + str(self.cell.column) + ')'
        ret += '\n faces: ' + str(len(self.faces))
        return ret

    def __repr__(self):
        return self.__str__()

    def add_face(self, vertices, vertices_levels=None, walls=None):
        if vertices_levels is None:
            vertices_levels = [0 for i in range(len(vertices))]
        f = CellVisual.Face()
        [f.add_vertex(v, v_level) for v, v_level in zip(vertices, vertices_levels)]
        f.walls = walls
        self.faces.append(f)

    def get_walls_with_vertex_weights(self):
        pass

    def get_faces_with_vertex_weights(self):
        return [f for f in self.faces if f.vertex_groups is not None]

    class Face:
        def __init__(self):
            self.vertices = []
            self.vertices_indices = []
            self.vertices_levels = []
            self.edges = []
            self.face = None
            self.vertex_groups = {}

            self.walls = None  # Edge walls
            self.walls_indices = None
            self.walls_vertex_groups = {}

        def corners(self):
            return len(self.vertices)

        def wall_corners(self):
            return [self.vertices[wall_ind] for wall_ind in self.walls] if self.walls else None

        def wall_vertices(self):
            return len(self.walls) if self.walls else 0

        def add_vertex(self, vec, level):
            self.vertices.append(vec)
            self.vertices_levels.append(level)

        def add_edges(self, delta):
            self.edges = [(delta + i, delta + ((i + 1) % self.corners())) for i in range(self.corners())]

        def add_face(self, delta):
            self.face = [delta + i for i in range(len(self.edges))]

        def translate_walls_indices(self, delta):
            self.walls_indices = [i + delta for i in range(len(self.walls))]

        def translate_indices(self, delta):
            self.add_edges(delta)
            self.add_face(delta)
            self.vertices_indices = [i + delta for i in range(len(self.vertices))]

        # def translate_vertices(self, delta):
        #     for v in self.vertices:
        #         v += delta

        def set_vertex_group(self, vertex_group_name, weights):
            self.vertex_groups[vertex_group_name] = weights

        def set_wall_vertex_groups(self, vertex_group_name, weights):
            self.walls_vertex_groups[vertex_group_name] = weights
