from functools import partial
from famapy.metamodels.fm_metamodel.models.fm_configuration import FMConfiguration
from famapy.metamodels.fm_metamodel.models.feature_model import FeatureModel

from famapy.metamodels.bdd_metamodel.models.bdd_model import BDDModel



class BDDHelper:

    def __init__(self, feature_model: FeatureModel, cnf_filepath: str):
        self.feature_model = feature_model
        self.bdd_model = BDDModel()
        self.bdd_model.from_cnf(cnf_filepath)

    def get_configurations(self, partial_configuration: FMConfiguration=None) -> list[FMConfiguration]:
        if partial_configuration is None:
            u = self.bdd_model.root
        else:
            expr = self.bdd_model.cnf_formula
            for f, selected in partial_configuration.elements.items():
                if selected:
                    expr += f' {BDDModel.AND} ' + f.name
                else:
                    expr += f' {BDDModel.AND} !' + f.name
            u = self.bdd_model.bdd.add_expr(expr)

        configs = []
        for c in self.bdd_model.bdd.pick_iter(u, care_vars=self.bdd_model.variables):
            print(c)
            elements = {self.feature_model.get_feature_by_name(f): True for f in c.keys() if c[f]}
            configs.append(FMConfiguration(elements))
        return configs
    
    def get_number_of_configurations(self, partial_configuration: FMConfiguration=None) -> int:
        if partial_configuration is None:
            return self.bdd_model.bdd.count(self.bdd_model.root, nvars=len(self.bdd_model.variables))

        expr = self.bdd_model.cnf_formula
        for f, selected in partial_configuration.elements.items():
            if selected:
                expr += f' {BDDModel.AND} ' + f.name
            else:
                expr += f' {BDDModel.AND} !' + f.name

        u = self.bdd_model.bdd.add_expr(expr)
        return self.bdd_model.bdd.count(u, nvars=len(self.bdd_model.variables))


