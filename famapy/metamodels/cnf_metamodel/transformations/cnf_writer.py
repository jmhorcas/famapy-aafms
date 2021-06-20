from famapy.core.models import VariabilityModel
from famapy.core.transformations import ModelToText

from famapy.metamodels.cnf_metamodel.models.cnf_model import CNFNotation


class CNFWriter(ModelToText):
    """Write the CNF formula as a string representing a feature model.

    Five different notations are available:
        Textual Symbols (default):
            (A) and (not B or C) and ...
        Java Symbols:
            (A) && (!B || C) && ...
        Java Short symbols:
            (A) & (!B | C) && ...
        Short Symbols:
            (A) & (-B | C) & ...
        Logical Symbols:
            (A) ∧ (¬B ∨ C) ∧ ...
    """

    @staticmethod
    def get_destination_extension() -> str:
        return "txt"

    def __init__(self, path: str, source_model: VariabilityModel) -> None:
        self._path = path
        self._source_model = source_model
        self._notation_syntax = CNFNotation.TEXTUAL  # Default notation

    def set_notation(self, cnf_output_syntax: CNFNotation):
        self._notation_syntax = cnf_output_syntax

    def transform(self) -> str:
        model = self._source_model.get_cnf_formula(self._notation_syntax)
        with open(self._path, 'w+', encoding='utf-8') as file:
            file.write(model)
        return model

