from pysat.solvers import Glucose3

from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from famapy.metamodels.pysat_metamodel.transformations.fm_to_pysat import FmToPysat

from famapy.metamodels.fm_metamodel.models.feature_model import FeatureModel, Feature
from famapy.metamodels.fm_metamodel.models.fm_configuration import FMConfiguration



class AAFMsHelper:

    def __init__(self, feature_model: FeatureModel, cnf_model: PySATModel = None):
        self.feature_model = feature_model
        if cnf_model is not None:
            self.cnf_model = cnf_model
        else:
            transform = FmToPysat(feature_model)
            self.cnf_model = transform.transform()
            
        #self.variables = {value: key for (key, value) in self.cnf_model.features.items()}
        #print(f"Variables: {self.variables}")
        self.solver = Glucose3()
        self.solver.append_formula(self.cnf_model.cnf)
        #print(f"CNF: {[c for c in self.cnf_model.cnf]}")
        #print(f"CNF features: {[c for c in self.cnf_model.features.items()]}")

    def is_valid_configuration(self, config: FMConfiguration) -> bool:
        variables = [value if config.is_selected(self.feature_model.get_feature_by_name(feature_name)) else -value for (value, feature_name) in self.cnf_model.features.items()]
        return self.solver.solve(assumptions=variables)

    def is_valid_partial_configuration(self, config: FMConfiguration) -> bool:
        variables = [self.cnf_model.variables[feature.name] if selected else -self.cnf_model.variables[feature.name] for (feature, selected) in config.elements.items() ]
        return self.solver.solve(assumptions=variables)

    def get_configurations(self) -> list[FMConfiguration]:
        solver = Glucose3()
        solver.append_formula(self.cnf_model.cnf)
        configurations = []
        for solutions in solver.enum_models():
            elements = dict()
            for variable in solutions:
                if variable > 0:  # This feature should appear in the product
                    feature = self.feature_model.get_feature_by_name(self.cnf_model.features[variable])
                    elements[feature] = True
            config = FMConfiguration(elements=elements)
            configurations.append(config)
        solver.delete()
        return configurations

    def get_products(self) -> list[FMConfiguration]:
        solver = Glucose3()
        solver.append_formula(self.cnf_model.cnf)
        configurations = []
        for solutions in solver.enum_models():
            elements = dict()
            for variable in solutions:
                if variable > 0:  # This feature should appear in the product
                    feature = self.feature_model.get_feature_by_name(self.cnf_model.features.get(variable))
                    if not feature.is_abstract:
                        elements[feature] = True
            config = FMConfiguration(elements=elements)
            configurations.append(config)
        solver.delete()
        return list(set(configurations))

    def get_core_features(self) -> set[Feature]:
        if not self.feature_model.root:  # void feature model
            return set()

        core_features = [self.feature_model.root]
        features = [self.feature_model.root]
        while features:
            f = features.pop()
            for relation in f.get_relations():
                if relation.is_mandatory():
                    core_features.extend(relation.children)
                    features.extend(relation.children)
        return set(core_features)
