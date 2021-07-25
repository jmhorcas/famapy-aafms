from abc import ABC, abstractmethod

from montecarlo_framework.models import State


class Algorithm(ABC):
    """Abstract algorithm that works with a search space of (States, Actions)."""

    @staticmethod
    @abstractmethod
    def get_name() -> str:
        """Name of the algorithm."""

    @abstractmethod
    def choose(self, state: State) -> State:
        """Return a new state from a given state."""

    @abstractmethod
    def run(self, state: State) -> State:
        """Execute the algorithm.
        
        The algorithm runs from a given state until a terminal state is found or
        until a stopping codition (e.g., time, memory, iterations) is meet.

        It returns the state solution.
        """

    @abstractmethod
    def solution_path(self) -> list[State]:
        """Return the list of states with the solution path
        from the initial state to the terminal state."""

    @abstractmethod
    def solution(self) -> State:
        """Return the state solution found."""
    
    @abstractmethod
    def cost(self) -> float:
        """Return the cost of finding the solution."""
