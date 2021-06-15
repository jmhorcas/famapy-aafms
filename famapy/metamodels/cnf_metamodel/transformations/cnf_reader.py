from famapy.core.transformations import TextToModel

from famapy.metamodels.cnf_metamodel.models.cnf_model import CNFModel


class CNFReader(TextToModel):
    """Read a CNF formula as a string representing a feature model.

    The expected format is the generated by FeatureIDE when exporting the model as CNF (.txt).
    That generates a file with the CNF formula in four different notations:
        Logical Symbols:
            (A) ∧ (¬B ∨ C) ∧ ...
        Textual Symbols:
            (A) and (not B or C) and ...
        Java Symbols:
            (A) && (!B || C) && ...
        Short Symbols:
            (A) & (-B | C) & ...
    
    The CNF Model is able to read any of these notations, but only one notation,
    so the .txt file should be modified to include only one of those notations by removing the others,
    leaving out only one line with the CNF formula in the file.
    """

    @staticmethod
    def get_source_extension() -> str:
        return 'txt'

    def __init__(self, path: str):
        self._path = path
        self.destination_model = CNFModel()

    def transform(self) -> CNFModel:
        """It assumes the CNF formula is defined in one line in the file."""
        with open(self._path, 'r', encoding='utf-8') as file:
            self.destination_model.from_cnf(file.readline())
        return self.destination_model

