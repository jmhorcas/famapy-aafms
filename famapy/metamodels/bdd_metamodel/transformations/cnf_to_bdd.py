from famapy.core.models import VariabilityModel
from famapy.core.transformations import ModelToModel

from famapy.metamodels.bdd_metamodel.models.bdd_model import BDDModel


class CNFToBDD(ModelToModel):
    
    @staticmethod
    def get_source_extension():
        return 'cnf'

    @staticmethod
    def get_destination_extension():
        return 'bdd'

    def __init__(self, source_model: VariabilityModel):
        self.source_model = source_model
        self.destination_model = BDDModel()

    def transform(self) -> BDDModel:
        self.destination_model.from_cnf(self.source_model.get_cnf_formula(BDDModel.CNF_NOTATION),
                                        self.source_model.get_variables())
        return self.destination_model

