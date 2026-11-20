"""Grafo genérico no dirigido: vértices hashables y recorridos sin ciclos infinitos."""
from collections import deque


class Graph:
    def __init__(self):
        self.adjacency = {}

    def __eq__(self, other):
        return isinstance(other, Graph) and self.adjacency == other.adjacency

    def add_node(self, node):
        if node in self.adjacency:
            return False
        self.adjacency[node] = []
        return True

    def add_edge(self, first, second):
        self.add_node(first)
        self.add_node(second)
        if second not in self.adjacency[first]:
            self.adjacency[first].append(second)
        if first not in self.adjacency[second]:
            self.adjacency[second].append(first)

    def remove_node(self, node):
        if node not in self.adjacency:
            return False
        for neighbor in list(self.adjacency[node]):
            self.adjacency[neighbor].remove(node)
        del self.adjacency[node]
        return True

    def neighbors(self, node):
        return list(self.adjacency.get(node, []))

    def bfs(self, start, neighbors=None):
        if start not in self.adjacency:
            return []
        neighbors = neighbors or self.neighbors
        queue, seen, result = deque([start]), {start}, []
        while queue:
            node = queue.popleft()
            result.append(node)
            for other in neighbors(node):
                if other not in seen:
                    seen.add(other)
                    queue.append(other)
        return result

    def dfs(self, start, neighbors=None):
        if start not in self.adjacency:
            return []
        neighbors = neighbors or self.neighbors
        stack, seen, result = [start], set(), []
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            result.append(node)
            stack.extend(reversed(neighbors(node)))
        return result

    def shortest_path(self, origin, destination, neighbors=None):
        if origin not in self.adjacency or destination not in self.adjacency:
            return []
        neighbors = neighbors or self.neighbors
        queue, previous = deque([origin]), {origin: origin}
        while queue:
            node = queue.popleft()
            if node == destination:
                path = []
                while node != origin:
                    path.append(node)
                    node = previous[node]
                path.append(origin)
                return path[::-1]
            for other in neighbors(node):
                if other not in previous:
                    previous[other] = node
                    queue.append(other)
        return []
