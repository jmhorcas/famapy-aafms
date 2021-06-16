import random 

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

    def get_random_sample(self, size: int, with_replacement: bool=False, partial_configuration: FMConfiguration=None) -> set[FMConfiguration]:
        """Return a uniforn random sample by enumerating all configurations."""
        configurations = self.get_configurations(partial_configuration)
        if with_replacement:
            return random.choices(configurations, k=size)
        return random.sample(configurations, k=size)

    def get_random_sample_uned_without_replacement(self, size: int, partial_configuration: FMConfiguration=None) -> set[FMConfiguration]:
        """Return a uniform random sample using the UNED BDD-based approach.
        
        This implementation only traverses the BDD once, but it only support sample with replacement.
        """
        if size < 0:
            raise ValueError('Sample is negative.')

        elements = {} if partial_configuration is None else partial_configuration.elements
        
        # Initialize the configurations and values for BDD nodes with already known features
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
    
    def get_random_sample_uned(self, size: int, with_replacement: bool=False, partial_configuration: FMConfiguration=None) -> list[FMConfiguration]:
        """Return a uniform random sample using the UNED BDD-based approach."""
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
        """Return a uniform random configuration using the UNED BDD-based approach."""
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