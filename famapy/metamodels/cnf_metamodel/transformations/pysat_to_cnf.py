from famapy.core.models import VariabilityModel
from famapy.core.transformations import ModelToModel
from famapy.metamodels.cnf_metamodel.models.cnf_model import CNFModel, CNFNotation, CNFLogicConnective


class PysatToCNF(ModelToModel):

    @staticmethod
    def get_source_extension():
        return 'pysat'

    @staticmethod
    def get_destination_extension():
        return 'cnf'

    def __init__(self, source_model: VariabilityModel):
        self.source_model = source_model
        self.counter = 1
        self.destination_model = CNFModel()
        self.cnf_notation = CNFNotation.JAVA_SHORT

    def transform(self) -> CNFModel:
        not_connective = self.cnf_notation.value[CNFLogicConnective.NOT]
        or_connective = ' ' + self.cnf_notation.value[CNFLogicConnective.OR] + ' '
        and_connective = ' ' + self.cnf_notation.value[CNFLogicConnective.AND] + ' '
        cnf_list = []
        for clause in self.source_model.get_all_clauses():
            cnf_list.append('(' + or_connective.join(list(map(lambda l: 
                not_connective + self.source_model.features[abs(l)] if l < 0 else 
                self.source_model.features[abs(l)], clause))) + ')')
                
        cnf_formula = and_connective.join(cnf_list)
        self.destination_model.from_cnf(cnf_formula)
        return self.destination_model
