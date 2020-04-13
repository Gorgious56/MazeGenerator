POLAR = '0'
TRIANGLE = '1'
SQUARE = '2'
HEXAGON = '3'

DEFAULT_CELL_TYPE = SQUARE


def generate_cell_type_enum():
    return [(POLAR, 'Polar', ''),
            (TRIANGLE, 'Triangle', ''),
            (SQUARE, 'Square', ''),
            (HEXAGON, 'Hexagon', '')
            ]


def get_cell_vertices(cell_type):
    if cell_type == POLAR:
        return 4
    elif cell_type == TRIANGLE:
        return 3
    elif cell_type == SQUARE:
        return 4
    elif cell_type == HEXAGON:
        return 6
    else:
        return 4
