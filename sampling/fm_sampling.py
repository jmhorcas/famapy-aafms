from abc import abstractmethod

from famapy.metamodels.fm_metamodel.models.fm_configuration import FMConfiguration
from famapy.metamodels.fm_metamodel.models.feature_model import FeatureModel

from sampling.sampling import Sampling


class FMSampling(Sampling):

    @abstractmethod
    def __init__(self, feature_model: FeatureModel):
        pass

    @abstractmethod
    def sample(self, size: int, with_replacement: bool=False) -> set[FMConfiguration]:
        pass    