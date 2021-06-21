from famapy.core.operations import Products

from famapy.metamodels.fm_metamodel.models import FeatureModel, FMConfiguration

from famapy.metamodels.bdd_metamodel.models.bdd_model import BDDModel


class BDDProducts(Products):
    """It computes all the products represented by the feature model using its BDD representation.
    
    It also supports the computation of all products from a partial configuration.
    """
    
    def __init__(self, bdd_model: BDDModel, partial_configuration: FMConfiguration=None) -> None:
        self.result = []
        self.feature_model = None
        self.bdd_model = bdd_model
        self.partial_configuration = partial_configuration
    
    def execute(self, feature_model: FeatureModel) -> 'BDDProducts':
        self.feature_model = feature_model
        self.result = self.get_products(self.partial_configuration)
        return self

    def get_result(self) -> list[FMConfiguration]:
        return self.result

    def get_products(self, partial_configuration: FMConfiguration=None) -> list[FMConfiguration]:
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
