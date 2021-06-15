from enum import Enum, auto

from famapy.core.models import VariabilityModel


class CNFLogicConnective(Enum):
    """The propositional logic connectives a formula in CNF can contain."""
    NOT = auto()
    AND = auto()
    OR = auto()


class CNFNotation(Enum):
    """Possible notations of a CNF formula."""
    LOGICAL = {CNFLogicConnective.NOT: '¬', CNFLogicConnective.AND: '∧', CNFLogicConnective.OR: '∨'}
    JAVA = {CNFLogicConnective.NOT: '!', CNFLogicConnective.AND: '&&', CNFLogicConnective.OR: '||'}
    SHORT = {CNFLogicConnective.NOT: '-', CNFLogicConnective.AND: '&', CNFLogicConnective.OR: '|'}
    TEXTUAL = {CNFLogicConnective.NOT: 'not', CNFLogicConnective.AND: 'and', CNFLogicConnective.OR: 'or'}


class CNFModel(VariabilityModel):
    """Representation of a variability model in conjunctive normal form (CNF).

    A CNF formula (or clausal normal form) is a conjunction of one or more clauses, 
    where a clause is a disjunction of literals.
    """

    @staticmethod
    def get_extension():
        return 'cnf'

    def __init__(self):
        self._cnf_formula = None
        self._cnf_notation = None
        self._variables = []  # list of str with features' names

    def from_cnf(self, cnf_formula: str):
        self._cnf_formula = cnf_formula
        self._cnf_notation = identify_notation(cnf_formula)
        self._variables = extract_variables(cnf_formula)

    def get_cnf_notation(self) -> CNFNotation:
        """Return the notation used for the CNF formula."""
        if self._cnf_formula is None:
            raise Exception("CNF Model not initialized. Use `from_cnf` method first.") 
        return self._cnf_notation

    def get_cnf_formula(self, cnf_output_syntax: CNFNotation=CNFNotation.JAVA) -> str:
        """Return the CNF formula in the specified notation syntax.

        Default syntax is CNFNotation.JAVA, that is, using connectives: !, and, or.
        """
        if self._cnf_formula is None:
            raise Exception("CNF Model not initialized. Use `from_cnf` method first.") 

        cnf_formula = self._cnf_formula
        cnf_notation = self._cnf_notation

        if cnf_output_syntax == cnf_notation:
            return cnf_formula
        
        # Translate AND operators
        symbol_pattern = ' ' + cnf_notation.value[CNFLogicConnective.AND] + ' '
        new_symbol = ' ' + cnf_output_syntax.value[CNFLogicConnective.AND] + ' '
        cnf_formula = cnf_formula.replace(symbol_pattern, new_symbol)

        # Translate OR operators
        symbol_pattern = ' ' + cnf_notation.value[CNFLogicConnective.OR] + ' '
        new_symbol = ' ' + cnf_output_syntax.value[CNFLogicConnective.OR] + ' '
        cnf_formula = cnf_formula.replace(symbol_pattern, new_symbol)

        # Translate NOT operators (this is more complex because the symbol may be part of a feature's name)
        if cnf_notation == CNFNotation.TEXTUAL:
            symbol_pattern = cnf_notation.value[CNFLogicConnective.NOT] + ' '
            new_symbol = cnf_output_syntax.value[CNFLogicConnective.NOT]
            cnf_formula = cnf_formula.replace(symbol_pattern, new_symbol)
        elif cnf_output_syntax == CNFNotation.TEXTUAL:
            symbol_pattern = ' ' + cnf_notation.value[CNFLogicConnective.NOT]
            new_symbol = ' ' + cnf_output_syntax.value[CNFLogicConnective.NOT] + ' '
            cnf_formula = cnf_formula.replace(symbol_pattern, new_symbol)

            symbol_pattern = '(' + cnf_notation.value[CNFLogicConnective.NOT]
            new_symbol = '(' + cnf_output_syntax.value[CNFLogicConnective.NOT] + ' '
            cnf_formula = cnf_formula.replace(symbol_pattern, new_symbol)
        else:
            symbol_pattern = ' ' + cnf_notation.value[CNFLogicConnective.NOT]
            new_symbol = ' ' + cnf_output_syntax.value[CNFLogicConnective.NOT]
            cnf_formula = cnf_formula.replace(symbol_pattern, new_symbol)

            symbol_pattern = '(' + cnf_notation.value[CNFLogicConnective.NOT]
            new_symbol = '(' + cnf_output_syntax.value[CNFLogicConnective.NOT]
            cnf_formula = cnf_formula.replace(symbol_pattern, new_symbol)
        return cnf_formula

    def get_variables(self) -> list[str]:
        """Return the list of variables' names in the CNF formula."""
        if self._cnf_formula is None:
            raise Exception("CNF Model not initialized. Use `from_cnf` method first.") 
        return self._variables


def identify_notation(cnf_formula: str) -> CNFNotation:
    """Return the notation used by the given CNF formula.

    Default CNFNotation.JAVA.
    """
    for notation in CNFNotation:
        for symbol in notation.value.values():
            symbol_pattern = ' ' + symbol + ' '
            if symbol_pattern in cnf_formula:
                return notation
    return CNFNotation.JAVA

def extract_variables(cnf_formula: str) -> list[str]:
    """Return the list of variables' names of the CNF formula."""
    variables = set()
    cnf_notation = identify_notation(cnf_formula)

    and_symbol_pattern = ' ' + cnf_notation.value[CNFLogicConnective.AND] + ' '
    clauses = list(map(lambda c: c[1:len(c)-1], cnf_formula.split(and_symbol_pattern)))  # Remove initial and final parenthesis

    # Remove final parenthesis of last clause (because of the possible end of line: '\n')
    if ')' in clauses[len(clauses)-1]:
        clauses[len(clauses)-1] = clauses[len(clauses)-1][:-1]  

    for c in clauses:
        tokens = c.split(' ')
        tokens = list(filter(lambda t: t != cnf_notation.value[CNFLogicConnective.OR], tokens))
        for feature in tokens:
            if feature == cnf_notation.value[CNFLogicConnective.NOT]:
                continue
            elif feature.startswith(cnf_notation.value[CNFLogicConnective.NOT]):
                variables.add(feature.replace(cnf_notation.value[CNFLogicConnective.NOT], '', 1))
            else:
                variables.add(feature)
    return list(variables)
    
