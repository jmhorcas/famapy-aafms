import queue

from montecarlo_framework.models import State
from montecarlo_framework.algorithms import Algorithm


class BreadthFirstSearch(Algorithm):

    def __init__(self):
        self.solution = None 
        self.solution_path = []
        self.cost = 0.0

    @staticmethod
    def get_name() -> str:
        return """Breadth-first search."""

    def choose(self, state: State) -> State:
        pass

    def run(self, state: State) -> State:
        solution_path = []
        cost = 0
        frontier = queue.Queue()
        frontier.put(state)
        explored = set()
        while not frontier.empty() and not state.is_terminal():
            state = frontier.get()
            explored.add(state)
            solution_path.append(state)
            for action in state.actions():
                children = state.successors(action)
                cost += action.cost(state)
                for child in children:
                    if child not in explored:
                        frontier.put(child)
        
        self.cost = cost 
        self.solution_path = solution_path
        self.solution = None if frontier.empty() else state
        return self.solution

    def solution_path(self) -> list[State]:
        return self.solution_path

    def solution(self) -> State:
        return self.solution
    
    def cost(self) -> float:
        return self.cost
