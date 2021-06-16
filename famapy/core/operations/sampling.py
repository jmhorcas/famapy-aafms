from abc import abstractmethod

from famapy.core.models import Configuration
from famapy.core.operations import Operation


class Sampling(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def sample(self, size: int, with_replacement: bool=False, partial_configuration: Configuration=None) -> list[Configuration]:
        pass  
