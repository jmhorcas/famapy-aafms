import heapq

from montecarlo_framework.models import State, StateValue, Node, Tree


class AStar():
    """Implementation of the A* search algorithm."""

    @staticmethod
    def get_name() -> str:
        return 'A Star'

    def __init__(self, initial_state: State):
        self.initial_state = initial_state
        self.tree = Tree()
        self.tree.add(Node(initial_state))

    def run(self) -> list[State]:
        heap = []
        state = self.initial_state

        while state is not None and not state.is_terminal():
            #print(f'Next state: {state}')
            for child in state.successors():
                cost = self.tree.get_node(state).cost + state.cost(child)
                if child not in self.tree or cost < self.tree.get_node(child).cost:
                    if child in self.tree:
                        heap.remove(StateValue(child))
                    heapq.heappush(heap, StateValue(child, cost + child.heuristic()))
                    self.tree.add(Node(child, state, cost))
            state = heapq.heappop(heap).state if heap else None
        return self.tree.path(state) if state is not None else None
