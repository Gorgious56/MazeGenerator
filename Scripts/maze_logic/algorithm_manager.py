from random import seed, choice, choices, random, shuffle, randrange
from math import ceil, hypot
from . data_structure . cells import CellPolar, CellTriangle, CellHex, Cell
from .. utils . priority_queue import PriorityQueue
from .. visual . cell_type_manager import POLAR, TRIANGLE, HEXAGON, SQUARE
from .. utils . union_find import UnionFind
from Scripts.utils import methods
from Scripts.maze_logic.data_structure import constants as cst


def work(grid, props):
    try:
        ALGORITHM_FROM_NAME[props.maze_algorithm](grid, props)
    except KeyError:
        pass


class MazeAlgorithm(object):
    name = 'NOT REGISTERED'
    weaved = True
    settings = ['maze_bias']

    def __init__(self, grid=None, props=None):
        self.grid = grid
        self.bias = props.maze_bias
        self._seed = props.seed
        seed(self._seed)
        self.__max_steps = 100000 if props.steps <= 0 else props.steps
        self.__steps = 0

    def is_last_step(self):
        self.__steps += 1
        return self.__steps >= self.__max_steps

    def add_template_passages(self):
        grid = self.grid
        if hasattr(grid, 'weave'):
            potential_passages = []
            for c in range(1, grid.columns - 1):
                for r in range(1, grid.rows - 1):
                    potential_passages.append(grid[c, r])
            shuffle(potential_passages)

            for pp in potential_passages[0: round(grid.weave * len(potential_passages))]:
                self.add_crossing(pp)

    def color_cells_by_tree_root(self):
        try:
            union_find = getattr(self, 'union_find')
            links = []
            for c in self.grid.all_cells():
                link = union_find.find(c)
                if link:
                    try:
                        c.group = links.index(link)
                    except ValueError:
                        links.append(link)
                        c.group = len(links) - 1
        except AttributeError:
            print('No Union Find Algorithm declared for this algorithm')

    def add_crossing(self, cell):
        can_cross = not cell.has_any_link()
        if can_cross:
            north = cell.neighbors[0]
            west = cell.neighbors[1]
            south = cell.neighbors[2]
            east = cell.neighbors[3]
            if random() > 0.5:  # Vertical underway
                pass
                cell.link(west)
                self.union_find.union(cell, east)
                cell.link(east)
                self.union_find.union(cell, east)

                new_cell_under = self.grid.tunnel_under(cell)
                self.union_find.data[new_cell_under] = new_cell_under

                north.link(north.neighbors[cell.neighbors_return[0]])
                self.union_find.union(north, north.neighbors[cell.neighbors_return[0]])
                south.link(south.neighbors[cell.neighbors_return[2]])
                self.union_find.union(south, south.neighbors[cell.neighbors_return[2]])
            else:
                cell.link(north)
                self.union_find.union(cell, north)
                cell.link(south)
                self.union_find.union(cell, south)

                new_cell_under = self.grid.tunnel_under(cell)
                self.union_find.data[new_cell_under] = new_cell_under

                west.link(west.neighbors[cell.neighbors_return[1]])
                self.union_find.union(west, west.neighbors[cell.neighbors_return[1]])
                east.link(east.neighbors[cell.neighbors_return[3]])
                self.union_find.union(east, east.neighbors[cell.neighbors_return[3]])


class BinaryTree(MazeAlgorithm):
    name = 'Binary Tree'
    weaved = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.union_find = UnionFind(self.grid.all_cells())

        self.run()

        self.color_cells_by_tree_root()

    def run(self):
        grid = self.grid
        bias = self.bias
        for c in grid.each_cell():
            c_type = type(c)
            if c_type is CellTriangle:
                if c.is_upright():
                    neighbors = [c.neighbor(0)] if c.row == grid.rows - 1 and c.neighbor(0) else [n for n in c.neighbors[0:2] if n]
                else:
                    neighbors = [c.neighbors[1]] if c.row == grid.rows - 1 and c.neighbors[1] else [n for n in [c.neighbors[2]] if n]
            elif c_type is CellHex:
                neighbors = [n for n in [c.neighbors[5 if c.column % 2 == 0 else 0]] if n] if c.row == grid.rows - 1 else [n for n in c.neighbors[0:3] if n]
            elif c_type is CellPolar:
                neighbors = c.outward
                if c.ccw and c.column != len(grid.rows_polar[c.row]) - 1:
                    neighbors.append(c.ccw)
            else:  # Square Cell
                neighbors = []
                for d in (cst.FWD, cst.RIGHT):
                    if c.neighbor(d):
                        neighbors.append(c.neighbor(d))
                if c.row == self.grid.rows - 1 and c.neighbor(cst.UP):
                    neighbors.append(c.neighbor_by_index(4))

            link_neighbor = methods.get_biased_choice(neighbors, bias, 5)
            if not self.union_find.connected(c, link_neighbor):
                c.link(link_neighbor)
                self.union_find.union(c, link_neighbor)

            if self.is_last_step():
                return


class Sidewinder(MazeAlgorithm):
    name = 'Sidewinder'
    weaved = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bias = (self.bias + 1) / 2

        self.union_find = UnionFind(self.grid.all_cells())

        self.run()
        self.color_cells_by_tree_root()

    def run(self):
        grid = self.grid
        for row in grid.each_row():
            run = []
            for c in row:
                link = None
                run.append(c)

                c_type = type(c)
                if c_type is CellTriangle:
                    if c.is_upright():
                        if c.neighbors[0]:
                            link = c, 0
                            # self.link(c, c.neighbors[0])
                        else:
                            if len(run) == 1:
                                link = c, 0
                                # c.link(c.neighbors[0])
                            else:
                                member = choice([c for c in run if not c.is_upright()])
                                if member.neighbors[2]:
                                    link = member, 1
                                    # self.link(member, member.neighbors[2])
                            run = []
                        if c.row == grid.rows - 1 and c.neighbors[1]:
                            link = c, 1
                            # self.link(c, c.neighbors[1])
                    else:
                        if (c.neighbors[1] is None) or (c.neighbors[1] is not None and self.must_close_run()):
                            member = choice([c for c in run if not c.is_upright()])
                            if member.neighbors[2]:
                                link = member, 2
                                # self.link(member, member.neighbors[2])
                            run = []
                        else:
                            self.link(c, c.neighbors[1])
                elif c_type is CellHex:
                    other = 5 if c.column % 2 == 0 else 0
                    if (c.neighbors[other] is None) or (c.neighbors[other] and self.must_close_run()):
                        member = choice(run)
                        north_neighbors = [n for n in c.neighbors[0:3] if n and not n.has_any_link()]
                        if north_neighbors:
                            link = member, choice(north_neighbors)
                            # self.link(member, choice(north_neighbors))
                        elif c.neighbors[5]:
                            link = c, other
                            # self.link(c, c.neighbors[other])
                        run = []
                    else:
                        link = c, other
                        # self.link(c, c.neighbors[other])
                elif c_type is CellPolar:
                    if (c.ccw and c.ccw.column == 0) or (c.has_outward_neighbor() and self.must_close_run()) or (c.row == 0):
                        member = choice(run)
                        if member.has_outward_neighbor():
                            link = member, choice(member.outward)
                        run = []
                    else:
                        link = c, c.ccw
                else:  # Cell is Square
                    if (c.neighbor(cst.RIGHT) is None) or (c.neighbor(cst.FWD) and self.must_close_run()):
                        member = choice(run)
                        if member.neighbors[0]:
                            link = member, 0
                        run = []
                    else:
                        link = c, 3

                if link:
                    self.link(link[0], link[1] if isinstance(link[1], Cell) else link[0].neighbor(link[1]))

                if self.is_last_step():
                    return

    def must_close_run(self):
        return self.bias > random()

    def link(self, cell_a, cell_b):
        cell_a.link(cell_b)
        self.union_find.union(cell_a, cell_b)


class Eller(MazeAlgorithm):
    name = 'Eller'
    weaved = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bias = (self.bias + 1) / 2

        self.union_find = UnionFind(self.grid.all_cells())

        self.run()

        self.color_cells_by_tree_root()

    def run(self):
        uf = self.union_find
        grid = self.grid
        for row in grid.each_row():
            sets_this_row = {}
            for c in row:
                if type(c) is CellPolar:
                    if c.inward and (c.row == grid.rows - 1 or (self.bias < random() and not uf.connected(c, c.inward))):
                        c.link(c.inward)
                        uf.union(c, c.inward)
                        if self.is_last_step():
                            return
                else:
                    if c.neighbors[3] and (c.row == grid.rows - 1 or (self.bias < random() and not uf.connected(c, c.neighbors[3]))):
                        c.link(c.neighbors[3])
                        uf.union(c, c.neighbors[3])
                        if self.is_last_step():
                            return
            for c in row:
                this_set = uf.find(c)
                try:
                    sets_this_row[this_set].append(c)
                except KeyError:
                    sets_this_row[this_set] = [c]
            if c.row != grid.rows - 1:
                for tree, cells in sets_this_row.items():
                    ch_len = min(len(cells), randrange(1, ceil(self.bias * len(cells) + 1)))
                    for c in choices(cells, k=ch_len):
                        if c.neighbors[0]:
                            c.link(c.neighbors[0])
                            uf.union(c, c.neighbors[0])
                            if self.is_last_step():
                                return


class CrossStitch(MazeAlgorithm):
    name = 'Cross-Stitch'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.expeditions = 1
        self.unvisited_legit_cells = []
        self.current = None

        self.run()

    def run(self):
        grid = self.grid
        _seed = self._seed
        direction = -1
        self.set_current(grid.random_cell(_seed))

        self.current.group = 1

        while self.current:
            unvisited_neighbor, direction = self.current.get_biased_unlinked_directional_neighbor(self.bias, direction)

            if unvisited_neighbor:
                self.link_to(self.current, unvisited_neighbor)
                self.set_current(unvisited_neighbor)
                if self.is_last_step():
                    return
            else:
                self.set_current(None)

            while self.unvisited_legit_cells:
                c = self.unvisited_legit_cells[0]
                if not c.has_any_link():
                    neighbor = c.get_biased_linked_neighbor(self.bias, 5)
                    if neighbor:
                        self.set_current(c)
                        self.link_to(self.current, neighbor)
                        if self.is_last_step():
                            return

    def link_to(self, c, other_c):
        c.link(other_c)
        try:
            self.unvisited_legit_cells.remove(other_c)
        except ValueError:
            pass
        try:
            self.unvisited_legit_cells.remove(c)
        except ValueError:
            pass
        other_c.group = self.expeditions + 2

    def set_current(self, c):
        self.current = c
        if c:
            c.group = self.expeditions
            unvisited_neighbors = self.current.get_unlinked_neighbors()
            self.add_to_unvisited_legit_cells(unvisited_neighbors)
        else:
            self.direction = - 1

    def add_to_unvisited_legit_cells(self, visited_cells):
        self.unvisited_legit_cells.extend([c for c in visited_cells if c not in self.unvisited_legit_cells])


class KruskalRandom(MazeAlgorithm):
    name = 'Kruskal Randomized'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.union_find = UnionFind(self.grid.all_cells())

        self.add_template_passages()

        self.run()
        self.color_cells_by_tree_root()

    def run(self):
        grid = self.grid
        unvisited_cells = grid.shuffled_cells()
        for c in unvisited_cells:
            for n in c.get_biased_neighbors(self.bias):
                if not self.union_find.connected(c, n):
                    c.link(n)
                    self.union_find.union(c, n)
                    if self.is_last_step():
                        return


class Prim(MazeAlgorithm):
    name = 'Prim'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bias = round((1 - abs(self.bias)) * 10)

        self.union_find = UnionFind(self.grid.all_cells())

        self.q = PriorityQueue()
        self.run()
        self.color_cells_by_tree_root()

    def run(self):
        start_cell = self.grid.random_cell()
        self.push_to_queue(start_cell)

        while not self.q.is_empty():
            cell, neighbor = self.q.pop()
            if not self.union_find.connected(cell, neighbor):
                cell.link(neighbor)
                self.union_find.union(cell, neighbor)
                if self.is_last_step():
                    return
                self.push_to_queue(neighbor)
            self.push_to_queue(cell)

    def push_neighbors_to_queue(self, cell):
        [self.push_to_queue(n) for n in cell.get_unlinked_neighbors()]

    def push_to_queue(self, cell, priority=None):
        try:
            self.q.push((cell, choice(cell.get_unlinked_neighbors())), priority if priority else (randrange(0, self.bias + 1)))
        except IndexError:
            pass


class GrowingTree(MazeAlgorithm):
    name = 'Growing Tree'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.weights = 0.5 - self.bias / 2, 0.5 + self.bias / 2

        self.run()

    def run(self):
        active_cells = [self.grid.random_cell()]

        while active_cells:
            cell = choices((self.last_element_in_list, choice), weights=self.weights)[0](active_cells)
            try:
                available_neighbor = choice(cell.get_unlinked_neighbors())
                cell.link(available_neighbor)
                active_cells.append(available_neighbor)
                if self.is_last_step():
                    return
            except IndexError:
                active_cells.remove(cell)

    def last_element_in_list(self, l):
        return l[-1] if l else None


class RecursiveDivision(MazeAlgorithm):
    name = 'Recursive Division'
    weaved = False
    settings = ['maze_bias']

    def __init__(self, grid, props=None, *args, **kwargs):
        super().__init__(grid=grid, props=props, *args, **kwargs)
        self.bias = (self.bias + 1) / 2

        self.union_find = UnionFind(self.grid.all_cells())

        self.run()

        self.color_cells_by_tree_root()

    def run(self):
        self.divide(0, 0, self.grid.rows, self.grid.columns)

    def divide(self, mx, my, ax, ay):
        HORIZONTAL, VERTICAL = 0, 1
        grid = self.grid

        dx = ax - mx
        dy = ay - my
        if dx < 2 or dy < 2:
            # make a hallway
            if dx > 1:
                y = my
                for x in range(mx, ax):
                    self.link(grid[y, x], 2)
                    if self.is_last_step():
                        return
            elif dy > 1:
                x = mx
                for y in range(my, ay):
                    self.link(grid[y, x], 3)
                    if self.is_last_step():
                        return
            return

        wall = HORIZONTAL if dy > dx else (VERTICAL if dx > dy else randrange(2))

        xp = methods.get_biased_choice(range(mx, ax - (wall == VERTICAL)), self.bias)
        yp = methods.get_biased_choice(range(my, ay - (wall == HORIZONTAL)), self.bias)

        if wall == HORIZONTAL:
            nx, ny = ax, yp + 1
            neighbor = 3
            ox, oy = mx, ny
        else:
            nx, ny = xp + 1, ay
            neighbor = 2
            ox, oy = nx, my
        if self.link(grid[yp, xp], neighbor):
            if self.is_last_step():
                return

        self.divide(mx, my, nx, ny)
        self.divide(ox, oy, ax, ay)

    def link(self, cell, neighbor_number):
        if cell:
            n = cell.neighbors[neighbor_number]
            # if n:
            if n and not self.union_find.connected(cell, n):
                cell.link(n)
                self.union_find.union(cell, n)
                return True
        return False


class RecursiveVoronoiDivision(MazeAlgorithm):
    name = 'Recursive Voronoi Division'
    settings = ['maze_room_size', 'maze_room_size_deviation']

    def __init__(self, grid, props=None, *args, **kwargs):
        super().__init__(grid=grid, props=props, *args, **kwargs)

        self.room_size = props.maze_room_size
        self.room_size_deviation = props.maze_room_size_deviation

        self.expeditions = 0

        all_cells = self.grid.all_cells().copy()

        # Destroy all walls:
        [[c.link(n, False) for n in c.get_neighbors() if n.level == c.level] for c in all_cells]
        self.run(all_cells)

    def run(self, cells):
        # Interpretation of https://rosettacode.org/wiki/Voronoi_diagram#Python with two points.
        # We could use actual sets for the data at the cost of determinism.
        if len(cells) <= max(2, randrange(int(self.room_size * (1 - (self.room_size_deviation / 100))), self.room_size + 1)):
            return

        # Choose two cells at random
        c_a, c_b = cells.pop(randrange(0, len(cells))), cells.pop(randrange(0, len(cells)))

        set_a, set_b, frontier = [c_a], [c_b], []

        # Build the voronoi diagram : Each set will contain the cell if it is closest to one of the randomly chosen point
        # There is a slight bias toward set_b but the calculation save is worth it
        [(set_a if hypot(c.column - c_a.column, c.row - c_a.row) < hypot(c.column - c_b.column, c.row - c_b.row) else set_b).append(c) for c in cells]

        # Add the frontier walls to a container
        [[frontier.append((c_set_a, c_set_b)) for c_set_b in [_n for _n in c_set_a.get_neighbors() if _n in set_b]] for c_set_a in set_a]
        # [[frontier.append((n, c)) for n in [_n for _n in c.get_neighbors() if _n in set_a]] for c in set_b]

        union_find_a = UnionFind(set_a)
        union_find_b = UnionFind(set_a)

        for c in set_a:
            c.group = self.expeditions
            for n in [n for n in c.get_neighbors() if n in set_a]:
                union_find_a.union(c, n)
        for c in set_b:
            c.group = self.expeditions
            for n in [n for n in c.get_neighbors() if n in set_b]:
                union_find_b.union(c, n)
        self.expeditions += 1

        # Unlink all the cells in the frontier but one
        if len(frontier) > 0:
            actual_psg = frontier.pop(randrange(0, len(frontier)))
            actual_psg[0].link(actual_psg[1])
            for psg in frontier:
                if self.is_last_step():
                    return
                # Make sure we don't close dead-ends or cells which got isolated from their set
                if len(psg[0].links) > 1 \
                        and len(psg[1].links) > 1\
                        and union_find_a.connected(psg[0], c_a) \
                        and union_find_b.connected(psg[1], c_b):
                    psg[0].unlink(psg[1])
            [self.run(s_x) for s_x in (set_a, set_b)]


class VoronoiDivision(MazeAlgorithm):
    name = 'Voronoi Division'
    settings = ['maze_room_size']

    def __init__(self, grid, props=None, *args, **kwargs):
        super().__init__(grid=grid, props=props, *args, **kwargs)

        self.room_size = props.maze_room_size
        self.room_size_deviation = props.maze_room_size_deviation
        self.rooms = grid.size // self.room_size

        all_cells = self.grid.all_cells().copy()

        shuffle(all_cells)
        self.union_find = UnionFind(all_cells)

        self.room_centers = all_cells[0:self.rooms]

        self.expeditions = 0

        # Destroy all walls:
        [[c.link(n, False) for n in c.get_neighbors() if n.level == c.level] for c in all_cells]
        self.run(all_cells)

    def run(self, cells):
        union_find = self.union_find

        frontiers = []
        [frontiers.append({}) for room in range(self.rooms)]

        for c in self.grid.all_cells():
            dmin = 100000000
            j = -1
            for i, r_c in enumerate(self.room_centers):
                d = hypot(r_c.column - c.column, r_c.row - c.row)
                if d < dmin:
                    dmin = d
                    j = i
            if j >= 0:
                union_find.union(c, self.room_centers[j])
                c.group = j

        cell_centers_union_groups = [union_find.find(c) for c in self.room_centers]

        for c in self.grid.all_cells():
            for n in [n for n in c.get_neighbors() if not union_find.connected(c, n)]:
                try:
                    frontiers[cell_centers_union_groups.index(union_find.find(c))][cell_centers_union_groups.index(union_find.find(n))].append((c, n))
                except KeyError:
                    frontiers[cell_centers_union_groups.index(union_find.find(c))][cell_centers_union_groups.index(union_find.find(n))] = [(c, n)]

        linked_cells = []
        for frontier_dic in frontiers:
            for ind, frontier in frontier_dic.items():
                already_open = False
                for lc in linked_cells:
                    if lc in frontier:
                        linked_cells.remove(lc)
                        already_open = True
                if frontier and not already_open:
                    actual_psg = frontier[randrange(0, len(frontier))]
                    if not union_find.connected(actual_psg[0], actual_psg[1]):
                        frontier.remove(actual_psg)
                        union_find.union(actual_psg[0], actual_psg[1])
                        linked_cells.append((actual_psg[1], actual_psg[0]))
                    for link in [link for link in frontier if len(link[0].links) > 1 and len(link[1].links) > 1]:
                        link[0].unlink(link[1])
                        if self.is_last_step():
                            return


class AldousBroder(MazeAlgorithm):
    name = 'Aldous-Broder'
    settings = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        grid = self.grid

        expeditions = 1
        current = grid.random_cell(self._seed, True)
        current.group = expeditions

        unvisited = grid.size - 1 - len(grid.masked_cells)
        while unvisited > 0:

            neighbor = choice(current.get_neighbors())

            if len(neighbor.links) <= 0:
                current.link(neighbor)
                unvisited -= 1
                if self.is_last_step():
                    return
            current = neighbor
            current.group = expeditions


class Wilson(MazeAlgorithm):
    name = 'Wilson'
    settings = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        grid = self.grid

        unvisited = grid.all_cells().copy()
        target_cell = choice(unvisited)
        unvisited.remove(target_cell)
        target_cell.group = -1

        while len(unvisited) > 0:
            cell = choice(unvisited)
            cell.group = 1
            path = [cell]

            while cell in unvisited:
                cell = choice([c for c in cell.neighbors if c != path[-1]])
                try:
                    path = path[0:path.index(cell) + 1]
                except ValueError:
                    path.append(cell)

            for i in range(0, len(path) - 1):
                path[i].link(path[i + 1])
                path[i].group = 1
                path[i + 1].group = 1
                unvisited.remove(path[i])
                if self.is_last_step():
                    return


class HuntAndKill(MazeAlgorithm):
    name = 'Hunt And Kill'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unvisited_legit_cells = []
        self.expeditions = 2
        self.direction = - 1

        self.run()

    def run(self):
        self.set_current(self.grid.random_cell(self._seed))

        self.add_to_unvisited_legit_cells(self.current.get_unlinked_neighbors())

        while self.current:
            while self.current:
                neighbor, self.direction = self.current.get_biased_unlinked_directional_neighbor(self.bias, self.direction)
                if neighbor:
                    self.link_to(self.current, neighbor)
                    self.set_current(neighbor)
                    if self.is_last_step():
                        return
                else:
                    self.current = None
            try:
                self.expeditions += 1
                self.set_current(choice(self.unvisited_legit_cells))
                neighbor = choice(self.current.get_linked_neighbors())
                self.link_to(neighbor, self.current)
                if self.is_last_step():
                    return

                self.direction = neighbor.get_direction(self.current)

                self.add_to_unvisited_legit_cells(self.current.get_unlinked_neighbors())
            except IndexError:  # Neighbors is empty
                break

    def link_to(self, c, other_c):
        c.link(other_c)
        try:
            self.unvisited_legit_cells.remove(other_c)
        except ValueError:
            pass
        try:
            self.unvisited_legit_cells.remove(c)
        except ValueError:
            pass
        other_c.group = self.expeditions

    def set_current(self, c):
        self.current = c
        c.group = self.expeditions
        unvisited_neighbors = self.current.get_unlinked_neighbors()
        self.add_to_unvisited_legit_cells(unvisited_neighbors)

    def add_to_unvisited_legit_cells(self, visited_cells):
        self.unvisited_legit_cells.extend([c for c in visited_cells if c not in self.unvisited_legit_cells])


class RecursiveBacktracker(MazeAlgorithm):
    name = 'Recursive Backtracker'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        expeditions = 1

        stack = [self.grid.random_cell(self._seed)]
        stack[-1].group = expeditions + 1

        backtracking = False
        direction = - 1

        while len(stack) > 0:
            current = stack[-1]

            unlinked_neighbor, direction = current.get_biased_unlinked_directional_neighbor(self.bias, direction)
            if unlinked_neighbor:
                current.link(unlinked_neighbor)
                if self.is_last_step():
                    return
                stack.append(unlinked_neighbor)
                unlinked_neighbor.group = expeditions + 1
                backtracking = False
            else:
                stack.pop()
                if backtracking:
                    current.group = - 1
                else:
                    expeditions += 1
                backtracking = True


ALGORITHMS = MazeAlgorithm.__subclasses__()
ALGORITHMS_NAMES = [alg_class.name for alg_class in ALGORITHMS]
ALGORITHM_FROM_NAME = {}
[ALGORITHM_FROM_NAME.update({alg_class.name: alg_class}) for alg_class in ALGORITHMS]
DEFAULT_ALGO = RecursiveBacktracker.name

WEAVED_ALGORITHMS = [algo.name for algo in ALGORITHMS if algo.weaved]


def is_algo_incompatible(props):
    if ALGORITHM_FROM_NAME[props.maze_algorithm] == AldousBroder and props.maze_space_dimension == '4':
        return "Aldous-Broder can't solve a box representation"
    if props.maze_space_dimension == '5' and props.maze_weave:
        return "Can't solve weaved maze for a box"
    return False


def is_algo_weaved(props):
    return props.cell_type == SQUARE and props.maze_algorithm in WEAVED_ALGORITHMS


def is_kruskal_random(algo_name):
    return algo_name == KruskalRandom.name


def generate_algo_enum():
    return [(alg_name, alg_name, '') for alg_name in ALGORITHMS_NAMES]
