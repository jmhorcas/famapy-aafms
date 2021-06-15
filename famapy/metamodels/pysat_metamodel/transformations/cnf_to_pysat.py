from famapy.core.models import VariabilityModel
from famapy.core.transformations import ModelToModel

from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel

from famapy.metamodels.cnf_metamodel.models.cnf_model import CNFLogicConnective


class CNFToPysat(ModelToModel):
    
    @staticmethod
    def get_source_extension():
        return 'cnf'

    @staticmethod
    def get_destination_extension():
        return 'pysat'

    def __init__(self, source_model: VariabilityModel):
        self.source_model = source_model
        self.counter = 1
        self.destination_model = PySATModel()
        self.cnf = self.destination_model.cnf

    def transform(self) -> PySATModel:
        self._read_clauses()
        return self.destination_model

    def _read_clauses(self):
        cnf_notation = self.source_model.get_cnf_notation()
        cnf_formula = self.source_model.get_cnf_formula(cnf_notation)

        and_symbol_pattern = ' ' + cnf_notation.value[CNFLogicConnective.AND] + ' '
        clauses = list(map(lambda c: c[1:len(c)-1], cnf_formula.split(and_symbol_pattern)))  # Remove initial and final parenthesis

        # Remove final parenthesis of last clause (because of the possible end of line: '\n')
        if ')' in clauses[len(clauses)-1]:
            clauses[len(clauses)-1] = clauses[len(clauses)-1][:-1]  

        for c in clauses:
            tokens = c.split(' ')
            tokens = list(filter(lambda t: t != cnf_notation.value[CNFLogicConnective.OR], tokens))
            logic_not = False
            cnf_clause = []
            for feature in tokens:
                if feature == cnf_notation.value[CNFLogicConnective.NOT]:
                    logic_not = True
                elif feature.startswith(cnf_notation.value[CNFLogicConnective.NOT]):
                    feature = feature.replace(cnf_notation.value[CNFLogicConnective.NOT], '', 1)
                    self._add_feature(feature)
                    cnf_clause.append(-1*self.destination_model.variables[feature])
                else:
                    self._add_feature(feature)
                    if logic_not:
                        cnf_clause.append(-1*self.destination_model.variables[feature])
                    else:
                        cnf_clause.append(self.destination_model.variables[feature])
                    logic_not = False
            self.destination_model.add_constraint(cnf_clause)

    def _add_feature(self, feature_name):
        if feature_name not in self.destination_model.variables.keys():
            self.destination_model.variables[feature_name] = self.counter
            self.destination_model.features[self.counter] = feature_name
            self.counter += 1
