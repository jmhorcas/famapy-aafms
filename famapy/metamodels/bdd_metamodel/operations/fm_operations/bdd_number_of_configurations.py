from famapy.core.operations import NumberOfConfigurations

from famapy.metamodels.fm_metamodel.models import FeatureModel, FMConfiguration

from famapy.metamodels.bdd_metamodel.models.bdd_model import BDDModel


class BDDNumberOfConfigurations(NumberOfConfigurations):
    """It computes the number of configurations of the feature model using its BDD representation.
    
    It also supports counting the configurations from a given partial configuration.
    """
    
    def __init__(self, bdd_model: BDDModel, partial_configuration: FMConfiguration=None) -> None:
        self.result = 0
        self.feature_model = None
        self.bdd_model = bdd_model
        self.partial_configuration = partial_configuration
    
    def execute(self, feature_model: FeatureModel) -> 'BDDNumberOfConfigurations':
        self.feature_model = feature_model
        self.result = self.get_number_of_configurations(self.partial_configuration)
        return self

    def get_result(self) -> int:
        return self.result

    def get_number_of_configurations(self, partial_configuration: FMConfiguration=None) -> int:
        if partial_configuration is None:
            u = self.bdd_model.root
            n_vars = len(self.bdd_model.variables)
        else:
            values = {f.name : selected for f, selected in partial_configuration.elements.items()}
            u = self.bdd_model.bdd.let(values, self.bdd_model.root)
            n_vars = len(self.bdd_model.variables) - len(values)
        
        return self.bdd_model.bdd.count(u, nvars=n_vars)
