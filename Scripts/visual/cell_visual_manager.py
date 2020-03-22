DISTANCE = 'DISTANCE'
GROUP = 'GROUP'
UNIFORM = 'UNIFORM'
NEIGHBORS = 'NEIGHBORS'
LONGEST_DISTANCE = 'LONGEST_DISTANCE'

DEFAULT_CELL_VISUAL_TYPE = DISTANCE


def generate_cell_visual_enum():
    return [(DISTANCE, 'Distance', ''),
            (GROUP, 'Cell Group', ''),
            (UNIFORM, 'Uniform', ''),
            (NEIGHBORS, 'Neighbors Amount', ''),
            ]
