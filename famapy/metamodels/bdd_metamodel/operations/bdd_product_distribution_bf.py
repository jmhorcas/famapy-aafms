from famapy.metamodels.fm_metamodel.models.fm_configuration import FMConfiguration
from famapy.core.operations import ProductDistribution

from famapy.metamodels.fm_metamodel.models import FeatureModel

from famapy.metamodels.bdd_metamodel.models import BDDModel
from famapy.metamodels.bdd_metamodel.operations import BDDProducts


class BDDProductDistributionBF(ProductDistribution):
    """The Product Distribution (PD) algorithm determines the number of products having a given number of features.

    This is a brute-force implementation that enumerates all products for accounting them.

    Ref.: [Heradio et al. 2019. Supporting the Statistical Analysis of Variability Models. SPLC. (https://doi.org/10.1109/ICSE.2019.00091)]
    """

    def __init__(self, bdd_model: BDDModel, partial_configuration: FMConfiguration=None) -> None:
        self.result = []
        self.feature_model = None
        self.partial_configuration = partial_configuration
        self.bdd_model = bdd_model
    
    def execute(self, feature_model: FeatureModel) -> 'BDDProductDistributionBF':
        self.feature_model = feature_model
        self.result = self.product_distribution(self.partial_configuration)
        return self

    def get_result(self) -> list[int]:
        return self.result

    def product_distribution(self, partial_configuration: FMConfiguration=None) -> list[int]:
        """It accounts for how many products have no features, one features, two features, ..., all features.

        It enumerates all products and filters them.
        """
        products = BDDProducts(self.bdd_model, self.partial_configuration).execute(self.feature_model).get_result()
        dist = []
        for i in range(len(self.bdd_model.variables)+1):
            dist.append(sum(len(p)==i for p in products))
        return dist

    