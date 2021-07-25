import copy 

from montecarlo_framework.models import State 


class ButtonMania(State):

    def __init__(self, n: int, k: int, values: list[list[int]]):
        assert len(values) == len(values[0]) == n
        self.values = values
        self.N = n 
        self.K = k

    def successors(self) -> list[State]:
        children = []
        for i in range(self.N):
            for j in range(self.N):
                new_values = copy.deepcopy(self.values)
                for row in range(-1, 2, 1):
                    for col in range(-1, 2, 1):
                        if row == 0 or col == 0:
                            x = i + row 
                            y = j + col
                            if x >= 0 and x < self.N and y >= 0 and y < self.N:
                                new_values[x][y] = self.K if new_values[x][y] == 0 else new_values[x][y]-1
                new_state = ButtonMania(self.N, self.K, new_values)
                children.append(new_state)
        return children

    def random_successor(self) -> State:
        pass

    def is_terminal(self) -> bool:
        return sum([e for sublist in self.values for e in sublist]) == 0

    def __hash__(self) -> int:
        return hash(tuple([e for sublist in self.values for e in sublist]))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ButtonMania):
            return False 
        return self.values == other.values 

    def __str__(self) -> str:
        return str(self.values)

    def cost(self, state: State) -> float:
        return 1.0

    def heuristic(self) -> float:
        return sum([e for sublist in self.values for e in sublist]) / 4 - 1

    def reward(self) -> float:
        return 1.0
