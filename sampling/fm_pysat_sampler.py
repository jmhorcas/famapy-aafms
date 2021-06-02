import random 

from famapy.metamodels.fm_metamodel.models.fm_configuration import FMConfiguration
from famapy.metamodels.fm_metamodel.models.feature_model import FeatureModel

from famapy.metamodels.pysat_metamodel.transformations.cnf_to_pysat import CNFReader, CNFNotation
from famapy.metamodels.pysat_metamodel.utils.aafms_helper import AAFMsHelper

from sampling.fm_sampling import FMSampling


class FMPySATSampling(FMSampling):
    """Uniform Random Sampling using the PySAT metamodel.
    
    It generates all possible configurations to guarantee uniform samples.
    This sampler is useful for testing purposes in small-size feature models.
    """

    def __init__(self, feature_model: FeatureModel):
        self.feature_model = feature_model
        self.configurations = None
        
    def fromCNF(self, cnf_model_filepath: str):
        # Read the feature model given as a CNF formula
        cnf_reader = CNFReader(cnf_model_filepath)
        cnf_model = cnf_reader.transform()
        cnf_formula = cnf_reader.get_cnf_formula(cnf_output_syntax=CNFNotation.JAVA)
        
        self.aafm = AAFMsHelper(self.feature_model, cnf_model)

    def sample(self, size: int) -> set[FMConfiguration]:
        if self.configurations is None:
            self.configurations = self.aafm.get_configurations()
        return random.sample(self.configurations, size)

    def delete(self):
        del self.configurations
        del self.aafm
        del self.feature_model

