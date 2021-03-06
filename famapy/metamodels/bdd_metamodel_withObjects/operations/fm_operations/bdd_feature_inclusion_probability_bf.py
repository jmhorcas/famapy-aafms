from famapy.metamodels.fm_metamodel.models import FeatureModel, Feature, FMConfiguration

from famapy.metamodels.bdd_metamodel.models import BDDModel
from famapy.metamodels.bdd_metamodel.operations import FeatureInclusionProbabilitly
from famapy.metamodels.bdd_metamodel.operations.fm_operations import BDDProducts


class BDDFeatureInclusionProbabilitlyBF(FeatureInclusionProbabilitly):
    """The Feature Inclusion Probability (FIP) operation determines the probability for a feature to be included in a valid product. 
    
    This is a brute-force implementation that enumerates all products for calculating the probabilities.
    
    Ref.: [Heradio et al. 2019. Supporting the Statistical Analysis of Variability Models. SPLC. (https://doi.org/10.1109/ICSE.2019.00091)]
    """

    def __init__(self, feature_model: FeatureModel, partial_configuration: FMConfiguration=None) -> None:
        self.result = []
        self.bdd_model = None
        self.feature_model = feature_model
        self.partial_configuration = partial_configuration
    
    def execute(self, bdd_model: BDDModel) -> 'BDDFeatureInclusionProbabilitlyBF':
        self.bdd_model = bdd_model
        self.result = self.feature_inclusion_probability(self.partial_configuration)
        return self

    def get_result(self) -> list[int]:
        return self.result

    def feature_inclusion_probability(self, partial_configuration: FMConfiguration=None) -> dict[Feature, float]:
        products = BDDProducts(self.feature_model, partial_configuration).execute(self.bdd_model).get_result()
        n_products = len(products)
        if n_products == 0:
            return {feature: 0.0 for feature in self.feature_model.get_features()}
            
        prob = {}
        for feature in self.feature_model.get_features():
            prob[feature] = sum(p.is_selected(feature) for p in products) / n_products
        return prob
