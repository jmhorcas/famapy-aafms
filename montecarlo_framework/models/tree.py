from montecarlo_framework.models import State, Node


class Tree():

    def __init__(self):
        self._tree = {}
    
    def add(self, node: Node):
        self._tree[node.state] = node

    def __contains__(self, state: State) -> bool:
        return state in self._tree

    def get_node(self, state: State) -> Node:
        return self._tree[state]

    def is_root(self, state: State) -> bool:
        return state in self._tree and self._tree[state].parent is None

    def path(self, state: State) -> list[State]:
        path = []
        while not self.is_root(state):
            path.insert(0, state)
            state = self._tree[state].parent
        path.insert(0, state)
        return path
