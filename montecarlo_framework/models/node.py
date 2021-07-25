from montecarlo_framework.models import State 


class Node():

    def __init__(self, state: State, parent: State = None, cost: float = 0.0):
        self.state = state
        self.parent = parent
        self.cost = cost
    
    # def __hash__(self) -> int:
    #     return hash(self.state)

    # def __eq__(self, other: object) -> bool:
    #     if not isinstance(other, Node):
    #         return False
    #     return self.state == other.state
