import random 

from famapy.core.operations.sampling import Sampling

from famapy.metamodels.fm_metamodel.models.fm_configuration import FMConfiguration
from famapy.metamodels.fm_metamodel.models.feature_model import FeatureModel


class BDDSampling(Sampling):
    """Uniform Random Sampling (URS) using a Binary Decision Diagram (BDD).
    
    This is a counting-based sampling inspired in the Knuth algorithm presented in Section 7.1.4 of
    [Donald E. Knuth. 2009. The Art of Computer Programming, 
    Volume 4, Fascicle 1: Bitwise Tricks & Techniques; Binary Decision Diagrams. 
    Addison-Wesley Professional.]

    Knuth showed how to accomplish uniform random sampling by subsequently partitioning the SAT solution space on variable assignments, 
    and then counting the number of solutions of the resulting parts. 

    The original algorithm by Knuth is specified on BDDs very efficiently, 
    as the probabilities required for all the possible SAT solutions are computed just once with a single BDD traversal, 
    and then reused every time a solution is generated. 
    Knuth’s algorithm can be also adapted to SAT technology.

    This is an adaptation to support samples with no replacement, therefore,
    it is not as efficient as the original Knuth’s algorithm because the BDD
    is traversed for each solution.

    Ref.: Heradio2020 [SPLC] - Uniform and scalable SAT-sampling for configurable systems (https://doi.org/10.1145/3382025.3414951)
    """

    def __init__(self, size: int, with_replacement: bool=False, partial_configuration: FMConfiguration=None) -> None:
        self.result = []
        self.size = size 
        self.with_replacement = with_replacement 
        self.partial_configuration = partial_configuration

    def sample(self, size: int, with_replacement: bool=False, partial_configuration: FMConfiguration=None) -> list[FMConfiguration]:
        nof_configs = self.get_number_of_configurations(partial_configuration)
        if size < 0 or (size > nof_configs and not with_replacement):
            raise ValueError('Sample larger than population or is negative.')

        configurations = []
        for _ in range(size):
            config = self.get_random_configuration(partial_configuration)
            configurations.append(config)
        if not with_replacement:
            configurations = list(set(configurations))
            while len(configurations) < size:
                config = self.get_random_configuration(partial_configuration)
                configurations.append(config)
        return configurations 

    def get_random_configuration(self, partial_configuration: FMConfiguration=None) -> FMConfiguration:
        # Initialize the configurations and values for BDD nodes with already known features
        elements = {} if partial_configuration is None else partial_configuration.elements
        values = {f.name : selected for f, selected in elements.items()}
        
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
            elements[self.feature_model.get_feature_by_name(feature)] = selected
            values[feature] = selected
            u = self.bdd_model.bdd.let({feature: selected}, u)
                
            n_vars -= 1
        return FMConfiguration(elements)

    def execute(self, model: FeatureModel) -> 'BDDSampling':
        self.feature_model = model
        self.result = self.sample(self.size, self.with_replacement, self.partial_configuration)
        return self

    def get_result(self) -> list[FMConfiguration]:
        return self.result

