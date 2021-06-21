import random 

from famapy.core.operations.sampling import Sampling

from famapy.metamodels.fm_metamodel.models.fm_configuration import FMConfiguration
from famapy.metamodels.fm_metamodel.models.feature_model import FeatureModel


class BDDSamplingWithRep(Sampling):
    """Uniform Random Sampling (URS) using a Binary Decision Diagram (BDD).
    
    This is an adaptation of 
    [Heradio et al. 2021. 
    Uniform and Scalable Sampling of Highly Configurable Systems. 
    Empirical Software Engineering]
    which relies on counting-based sampling inspired in the original Knuth algorithm.

    This implementation only supports sample with replacement.
    """

    def __init__(self, size: int, partial_configuration: FMConfiguration=None) -> None:
        self.result = []
        self.size = size 
        self.partial_configuration = partial_configuration

    def sample(self, size: int, partial_configuration: FMConfiguration=None) -> list[FMConfiguration]:
        if size < 0:
            raise ValueError('Sample is negative.')

        # Initialize the configurations and values for BDD nodes with already known features
        elements = {} if partial_configuration is None else partial_configuration.elements
        values = {f.name : selected for f, selected in elements.items()}
        # Set the BDD nodes with the already known features values
        u = self.bdd_model.bdd.let(values, self.bdd_model.root)

        configurations = [{} | elements for _ in range(size)]  
        configurations_values = [{} | values for _ in range(size)]
        configurations_u = [u for _ in range(size)]

        care_vars = set(self.bdd_model.variables) - values.keys()
        n_vars = len(care_vars)
        for feature in care_vars:
            for i in range(size):
                values = configurations_values[i]
                u = configurations_u[i]

                # Number of configurations with the feature selected
                v_sel = self.bdd_model.bdd.let({feature: True}, u)
                nof_configs_var_selected = self.bdd_model.bdd.count(v_sel, nvars=n_vars-1)
                # Number of configurations with the feature unselected
                v_unsel = self.bdd_model.bdd.let({feature: False}, u)
                nof_configs_var_unselected = self.bdd_model.bdd.count(v_unsel, nvars=n_vars-1)

                # Randomly select or not the feature
                selected = random.choices([True, False], [nof_configs_var_selected, nof_configs_var_unselected], k=1)[0]
                
                # Update configuration and BDD node for the new feature
                configurations[i][self.feature_model.get_feature_by_name(feature)] = selected
                configurations_values[i][feature] = selected
                configurations_u[i] = self.bdd_model.bdd.let({feature: selected}, u)

            n_vars -= 1
        return {FMConfiguration(elements) for elements in configurations}

    def execute(self, model: FeatureModel) -> 'BDDSamplingWithRep':
        self.feature_model = model
        self.result = self.sample(self.size, self.partial_configuration)
        return self

    def get_result(self) -> list[FMConfiguration]:
        return self.result

