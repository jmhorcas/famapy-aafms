try:
    from dd.cudd import BDD
except ImportError:
    from dd.autoref import BDD

from famapy.metamodels.pysat_metamodel.transformations.cnf_to_pysat import CNFReader, CNFNotation, LogicOperator


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


class BDDModel:
    """A Binary Decision Diagram (BDD) representation of the feature model given as a CNF formula.

    It relies on the dd module: https://pypi.org/project/dd/
    """

    NOT = CNFNotation.JAVA.value[LogicOperator.NOT]
    AND = CNFNotation.JAVA.value[LogicOperator.AND]
    OR = CNFNotation.JAVA.value[LogicOperator.OR]

    def __init__(self):
        pass 

    def from_cnf(self, cnf_filepath: str):
        # Read the feature model given as a CNF formula
        cnf_reader = CNFReader(cnf_filepath)
        cnf_model = cnf_reader.transform()
        self.cnf_formula = cnf_reader.get_cnf_formula(cnf_output_syntax=CNFNotation.JAVA)

        # BDD manager
        self.bdd = BDD()

        # Declare variables
        for v in cnf_model.variables.keys():
            self.bdd.declare(v)

        # Build the BDD
        self.root = self.bdd.add_expr(self.cnf_formula)
        self.variables = cnf_model.variables.keys()

        # Store the variable order
        self.variable_order = {self.bdd.level_of_var(var): var for var in cnf_model.variables.keys()}

    def serialize(self, filename: str, format: str):
        """Write BDDs to `filename`.

        The format can be:
        - dddmp v3: `'.dddmp'`
        - dddmp v2: `'.dddmp2'`
        - PDF: `'.pdf'`
        - PNG: `'.png'`
        - SVG: `'.svg'`
        """
        self.bdd.dump(filename=filename, roots=None, filetype=format)

        if format == '.dddmp':
             # Convert to dddmp format version 3.0 (adding the '.varnames' field)
            dddmp_v2_to_v3(filename)
    
    