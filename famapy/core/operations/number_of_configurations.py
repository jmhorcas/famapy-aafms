from abc import abstractmethod

from famapy.core.operations import Operation
from famapy.core.models import Configuration


class NumberOfConfigurations(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_number_of_configurations(self, partial_configuration: Configuration=None) -> int:
        pass
