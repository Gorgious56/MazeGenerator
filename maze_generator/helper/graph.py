from collections import defaultdict
from typing import Iterable

from maze_generator.helper.union_find import UnionFind

# https://stackoverflow.com/a/30747003/7092409


class OrderedGraph:
    """Graph data structure, undirected by default."""

    def __init__(self, connections=None, nodes=None):
        self._graph = defaultdict(dict)
        if connections:
            self.add_connections(connections)
        if nodes:
            for node in nodes:
                self._graph[node] = {}
        self._union_find = UnionFind(self.nodes)

    def add_connections(self, connections: Iterable[tuple]):
        """Add connections (list of tuple pairs) to graph"""
        for node_a, node_b in connections:
            self.connect(node_a, node_b)

    def disconnect(self, node_a, node_b):
        """Bidirectionally disconnects two nodes"""
        self._graph[node_a].pop(node_b, None)
        self._graph[node_b].pop(node_a, None)

    def connect(self, node1, node2):
        """Add connection between node1 and node2"""
        if node2 not in self._graph[node1]:
            self._graph[node1][node2] = False
        if node1 not in self._graph[node2]:
            self._graph[node2][node1] = False

    def link(self, node1, node2):
        """Add link between node1 and node2"""
        self._graph[node1][node2] = True
        self._graph[node2][node1] = True
        self._union_find.union(node1, node2)

    def unlink(self, node1, node2):
        self._graph[node1][node2] = False
        self._graph[node2][node1] = False
        self._union_find.ungroup(node1, node2)

    @property
    def nodes(self):
        return self._graph.keys()

    @property
    def nodes_with_at_least_one_neighbor(self):
        for node, neighbors in self._graph.items():
            if neighbors:
                yield node

    @property
    def nodes_with_at_least_one_link(self):
        for node, neighbors in self._graph.items():
            for _, link in neighbors.items():
                if link:
                    yield node
                    break

    def remove(self, node):
        """Remove all references to node"""
        for n, cxns in self._graph.items():
            cxns.pop(node, None)
        self._graph.pop(node, None)

    def connected(self, node1, node2):
        """Can node1 be linked to node2"""
        return node1 in self._graph and node2 in self._graph[node1]

    def linked(self, node1, node2):
        """Is node1 directly linked to node2"""
        return self.connected(node1, node2) and self._graph[node1][node2] and self._graph[node2][node1]

    @property
    def links(self):
        links = set()
        for node, neighbors in self._graph.items():
            for neighbor, link in neighbors.items():
                if link and (neighbor, node) not in links:
                    links.add((node, neighbor))
        return links

    @property
    def connections_with_no_link(self):
        connections_with_no_link = set()
        for node, neighbors in self._graph.items():
            for neighbor, link in neighbors.items():
                if not link and (neighbor, node) not in connections_with_no_link:
                    connections_with_no_link.add((node, neighbor))
        return connections_with_no_link

    def is_linked(self, node):
        for state in self.get_state(node).values():
            if state:
                return True

    def get_state(self, node):
        return self._graph[node]

    def get_neighbors(self, node):
        return self.get_state(node).keys()

    def edge_value(self, node, neighbor):
        return self.get_state(node)[neighbor]

    def are_reachable(self, node1, node2):
        return self._union_find.connected(node1, node2)

    def find_path(self, node1, node2, path=[]):
        """Find any path between node1 and node2 (may not be shortest)"""
        path = path + [node1]
        if node1 == node2:
            return path
        if node1 not in self._graph:
            return None
        for node in self._graph[node1]:
            if node not in path:
                new_path = self.find_path(node, node2, path)
                if new_path:
                    return new_path
        return None

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, dict(self._graph))

    def __eq__(self, other):
        return self._graph == other._graph
