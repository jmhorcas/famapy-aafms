import random 

from famapy.core.operations.sampling import Sampling

from famapy.metamodels.fm_metamodel.models import FeatureModel, FMConfiguration

from famapy.metamodels.bdd_metamodel.models import BDDModel
from famapy.metamodels.bdd_metamodel.operations.fm_operations import BDDNumberOfConfigurations


class BDDSampling(Sampling):
    """Uniform Random Sampling (URS) using a Binary Decision Diagram (BDD).
    
    This is an adaptation of 
    [Heradio et al. 2021. 
    Uniform and Scalable Sampling of Highly Configurable Systems. 
    Empirical Software Engineering]
    which relies on counting-based sampling inspired in the original Knuth algorithm.

    This implementation supports samples with no replacement as well as samples from a partial configuration.
    """

    def __init__(self, feature_model: FeatureModel, size: int, with_replacement: bool=False, partial_configuration: FMConfiguration=None) -> None:
        self.result = []
        self.bdd_model = None
        self.feature_model = feature_model
        self.size = size 
        self.with_replacement = with_replacement 
        self.partial_configuration = partial_configuration

    def execute(self, bdd_model: BDDModel) -> 'BDDSampling':
        self.bdd_model = bdd_model
        self.result = self.sample(self.size, self.with_replacement, self.partial_configuration)
        return self

    def get_result(self) -> list[FMConfiguration]:
        return self.result

    def sample(self, size: int, with_replacement: bool=False, partial_configuration: FMConfiguration=None) -> list[FMConfiguration]:
        nof_configs = BDDNumberOfConfigurations(self.feature_model, partial_configuration).execute(self.bdd_model).get_result()
        if size < 0 or (size > nof_configs and not with_replacement):
            raise ValueError('Sample larger than population or is negative.')

        configurations = []
        for _ in range(size):
            config = self.get_random_configuration(partial_configuration)
            configurations.append(config)

        if not with_replacement:
            configurations = set(configurations)
            while len(configurations) < size:
                config = self.get_random_configuration(partial_configuration)
                configurations.add(config)

        return list(configurations)

    def get_random_configuration(self, partial_configuration: FMConfiguration=None) -> FMConfiguration:
        # Initialize the configurations and values for BDD nodes with already known features
        values = {} if partial_configuration is None else {f.name: selected for f, selected in partial_configuration.elements.items()}
        features = {} if partial_configuration is None else {f: selected for f, selected in partial_configuration.elements.items()}

        # Set the BDD nodes with the already known features values
        u = self.bdd_model.bdd.let(values, self.bdd_model.root)

        care_vars = set(self.bdd_model.variables) - values.keys()
        n_vars = len(care_vars)
        for feature in care_vars:
            # Number of configurations with the feature selected
            v_sel = self.bdd_model.bdd.let({feature: True}, u)
            nof_configs_var_selected = self.bdd_model.bdd.count(v_sel, nvars=n_vars-1)
            # Number of configurations with the feature unselected
            v_unsel = self.bdd_model.bdd.let({feature: False}, u)
            nof_configs_var_unselected = self.bdd_model.bdd.count(v_unsel, nvars=n_vars-1)

            # Randomly select or not the feature
            selected = random.choices([True, False], [nof_configs_var_selected, nof_configs_var_unselected], k=1)[0]

            # Update configuration and BDD node for the new feature
            values[feature] = selected
            features[self.feature_model.get_feature_by_name(feature)] = selected
            u = self.bdd_model.bdd.let({feature: selected}, u)
                
            n_vars -= 1
        return FMConfiguration(features)
