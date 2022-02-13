from maze_generator.helper.graph import OrderedGraph


def new(connections=None):
    if connections is None:
        connections = [((0, 0, 0), (1, 0, 0))]
    return OrderedGraph(connections)


def new_grid(columns, rows):
    nodes = []
    for x in range(columns):
        for y in range(rows):
            nodes.append((x, y))
    connections = []
    for x in range(columns):
        for y in range(rows):
            if x < columns - 1:
                connections.append(((x, y), (x + 1, y)))
            if y < rows - 1:
                connections.append(((x, y), (x, y + 1)))

    return OrderedGraph(connections=connections)
