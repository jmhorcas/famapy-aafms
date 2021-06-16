from famapy.metamodels.fm_metamodel.models.fm_configuration import FMConfiguration
from famapy.metamodels.fm_metamodel.models.feature_model import FeatureModel

from famapy.metamodels.bdd_metamodel.models.bdd_model import BDDModel


class BDDHelper:

    def __init__(self, feature_model: FeatureModel, bdd_model: BDDModel):
        self.feature_model = feature_model
        self.bdd_model = bdd_model

    def get_configurations(self, partial_configuration: FMConfiguration=None) -> list[FMConfiguration]:
        if partial_configuration is None:
            u = self.bdd_model.root
            care_vars = self.bdd_model.variables
            elements = {}
        else:
            values = {f.name : selected for f, selected in partial_configuration.elements.items()}
            u = self.bdd_model.bdd.let(values, self.bdd_model.root)
            care_vars = set(self.bdd_model.variables) - values.keys()
            elements = partial_configuration.elements
        
        configs = []
        for c in self.bdd_model.bdd.pick_iter(u, care_vars=care_vars):
            features = {self.feature_model.get_feature_by_name(f): True for f in c.keys() if c[f]}
            features = features | elements
            configs.append(FMConfiguration(features))
        return configs
    
    def get_number_of_configurations(self, partial_configuration: FMConfiguration=None) -> int:
        if partial_configuration is None:
            u = self.bdd_model.root
            n_vars = len(self.bdd_model.variables)
        else:
            values = {f.name : selected for f, selected in partial_configuration.elements.items()}
            u = self.bdd_model.bdd.let(values, self.bdd_model.root)
            n_vars = len(self.bdd_model.variables) - len(values)
        
        return self.bdd_model.bdd.count(u, nvars=n_vars)

