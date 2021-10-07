from famapy.core.models import Configuration

from famapy.metamodels.bdd_metamodel.models import BDDModel
from famapy.metamodels.bdd_metamodel.operations import ProductDistribution, BDDProducts


class BDDProductDistributionBF(ProductDistribution):
    """The Product Distribution (PD) algorithm determines the number of solutions having a given number of variables.

    This is a brute-force implementation that enumerates all solutions for accounting them.

    Ref.: [Heradio et al. 2019. Supporting the Statistical Analysis of Variability Models. SPLC. (https://doi.org/10.1109/ICSE.2019.00091)]
    """

    def __init__(self, partial_configuration: Configuration=None) -> None:
        self.result = []
        self.partial_configuration = partial_configuration
    
    def execute(self, bdd_model: BDDModel) -> 'BDDProductDistributionBF':
        self.bdd_model = bdd_model
        self.result = self.product_distribution(self.partial_configuration)
        return self

    def get_result(self) -> list[int]:
        return self.result

    def product_distribution(self, partial_configuration: Configuration=None) -> list[int]:
        """It accounts for how many solutions have no variables, one variable, two variables, ..., all variables.

        It enumerates all solutions and filters them.
        """
        products = BDDProducts(partial_configuration).execute(self.bdd_model).get_result()
        dist = []
        for i in range(len(self.bdd_model.variables)+1):
            dist.append(sum(len(p.elements)==i for p in products))
        return dist
