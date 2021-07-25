from functools import total_ordering

from montecarlo_framework.models import State


@total_ordering
class StateValue():

    def __init__(self, state: State, value: float = 0.0):
        self.state = state
        self.value = value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, StateValue) and self.state == other.state

    def __lt__(self, other: object):
        return self.value < other.value
