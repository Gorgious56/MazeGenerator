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
