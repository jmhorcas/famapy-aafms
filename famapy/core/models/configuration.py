from typing import Any


class Configuration():

    def __init__(self, elements: dict[Any, bool]) -> None:
        self.elements = elements

    def __eq__(self, other: 'Configuration') -> bool:
        return self.elements == other.elements

    def __hash__(self) -> int:
        return hash(frozenset(self.elements.items()))

    def __str__(self) -> str:
        return str([str(e) for e in self.elements.keys() if self.elements[e]])
