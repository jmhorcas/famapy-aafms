from enum import Enum

from dd.autoref import Function

from famapy.core.transformations import ModelToText

from famapy.metamodels.bdd_metamodel.models.bdd_model import BDDModel


class BDDDumpFormat(Enum):
    """Possible output format for representing a BDD."""
    DDDMPv3 = 'dddmp'
    DDDMPv2 = 'dddmp2'
    PDF = 'pdf'
    PNG = 'png'
    SVG = 'svg'

class BDDWriter(ModelToText):
    """Create the dump file representing the argument BDD.
    
    The format can be:
        - dddmp v3: `'.dddmp'` (default)
        - dddmp v2: `'.dddmp2'`
        - PDF: `'.pdf'`
        - PNG: `'.png'`
        - SVG: `'.svg'`
    """

    @staticmethod
    def get_destination_extension() -> str:
        return BDDDumpFormat.DDDMPv3

    def __init__(self, path: str, source_model: BDDModel, roots: list[Function]=None, output_format: BDDDumpFormat=BDDDumpFormat.DDDMPv3) -> None:
        self._path = path
        self._source_model = source_model
        self._output_format = output_format
        self._roots = roots

    def set_format(self, output_format: BDDDumpFormat):
        self._output_format = output_format
    
    def set_roots(self, roots: list[Function]):
        self._roots = roots

    def transform(self) -> None:
        self._source_model.bdd.dump(filename=self._path, roots=self._roots)
        if self._output_format == BDDDumpFormat.DDDMPv3:
             # Convert to dddmp format version 3.0 (adding the '.varnames' field)
            dddmp_v2_to_v3(self._path)
        return None

def dddmp_v2_to_v3(filepath: str):
    """Convert the file with the BDD dump in format dddmp version 2 to version 3.

    The difference between versions 2.0 and 3.0 is the addition of the '.varnames' field.
    """

    with open(filepath, 'r') as file:
        lines = file.readlines()
        # Change version from 2.0 to 3.0
        i, line = next((i,l) for i, l in enumerate(lines) if '.ver DDDMP-2.0' in l)
        lines[i] = line.replace('2.0', '3.0')

        # Add '.varnames' field
        i, line = next((i,l) for i, l in enumerate(lines) if '.orderedvarnames' in l)
        lines.insert(i-1, line.replace('.orderedvarnames', '.varnames'))

    with open(filepath, 'w') as file:
        file.writelines(lines)