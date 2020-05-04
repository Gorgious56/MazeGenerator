POLAR = '0'
TRIANGLE = '1'
SQUARE = '2'
HEXAGON = '3'
OCTOGON = '4'

DEFAULT_CELL_TYPE = SQUARE


def generate_cell_type_enum():
    return [(POLAR, 'Polar', ''),
            (TRIANGLE, 'Triangle', ''),
            (SQUARE, 'Square', ''),
            (HEXAGON, 'Hexagon', ''),
            (OCTOGON, 'Octogon', ''),
            ]
