from abc import ABC, abstractmethod


class State(ABC):
    """
    Representation of problems for searching strategies.
    
    A representation of a state space must include the representation of the states themselves, 
    as well as the transitions or set of states directly accessible 
    from a give state (i.e., the successors).
    
    Each kind of problem must extend this class to represent its states.
    """

    @abstractmethod
    def successors(self) -> list['State']:
        """All possible successors of this state."""

    @abstractmethod
    def random_successor(self) -> 'State':
        """Random successor of this state (redefine it for efficiency)."""

    @abstractmethod
    def is_terminal(self) -> bool:
        """Returns True if the state represents a terminal node (the goal of the problem)."""

    @abstractmethod
    def __hash__(self) -> int:
        """States must be hashable."""

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        """States must be comparable."""

    @abstractmethod
    def cost(self, state: 'State') -> float:
        """Cost of the transition `self` -> state."""

    @abstractmethod
    def heuristic(self) -> float:
        """Heuristic estimation of the cost from `self` to the goal."""

    @abstractmethod
    def reward(self) -> float:
        """Assumes `self` is terminal node. Examples of reward: 1=win, 0=loss, .5=tie, etc."""
