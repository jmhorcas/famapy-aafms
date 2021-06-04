from abc import abstractmethod

from famapy.core.models.configuration import Configuration
from famapy.core.models.variability_model import VariabilityModel


class Sampling():

    @abstractmethod
    def __init__(self, model: VariabilityModel):
        pass

    @abstractmethod
    def sample(self, size: int, with_replacement: bool=False) -> set[Configuration]:
        pass    