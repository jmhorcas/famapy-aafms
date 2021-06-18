from collections import defaultdict
from dd.autoref import BDD, Function

from famapy.metamodels.cnf_metamodel.models.cnf_model import CNFNotation, CNFLogicConnective


class BDDModel:
    """A Binary Decision Diagram (BDD) representation of the feature model given as a CNF formula.

    It relies on the dd module: https://pypi.org/project/dd/
    """

    CNF_NOTATION = CNFNotation.JAVA_SHORT
    NOT = CNF_NOTATION.value[CNFLogicConnective.NOT]
    AND = CNF_NOTATION.value[CNFLogicConnective.AND]
    OR = CNF_NOTATION.value[CNFLogicConnective.OR]

    def __init__(self):
        self.bdd = BDD()  # BDD manager
        self.cnf_formula = None
        self.reference = None 
        self.root = None
        self.variables = []
        self.variable_order = {} 

    def from_cnf(self, cnf_formula: str, variables: list[str]):
        self.cnf_formula = cnf_formula
        self.variables = variables

        # Declare variables
        for v in self.variables:
            self.bdd.declare(v)

        # Build the BDD
        self.reference = self.bdd.add_expr(self.cnf_formula)
        root_var = self.bdd.var_at_level(0)
        self.root = self.bdd.var(root_var)
        #self.root = self.reference

        # Reorder variables
        # variable_order = self.bdd.vars 
        # new_order = sorted(variable_order.keys())
        # new_variable_order = {v: variable_order[v] for v in new_order} 

        # variable_order = {var: self.bdd.level_of_var(var) for var in self.variables}
        # var = self.bdd.var_at_level(0)
        # level = self.reference.level
        # variable_order[self.reference.var] = 0
        # variable_order[var] = level
        # self.bdd.reorder(variable_order)
        # self.variable_order = {var: self.bdd.level_of_var(var) for var in self.variables}

        # Store the root
        #self.root = self.get_root()
        #self.reference = self.root

    # def get_root(self):
    #     for v in self.bdd.vars:
    #         node = self.bdd.var(v)
    #         if node.level == 0:
    #             return node
    #     return None

    def index(self, n: Function) -> int:
        """Position of the variable that labels the node `n` in the ordering.
            
        Example: node `n4` is labeled `B`, and `B` is in the second position of the ordering `[A,B,C]`.
        thus var(n4) = 2.
        """
        if n.node == -1 or n.node == 1:  # index(n0) = index(n1) = s + 1, being s the number of variables.
            return len(self.bdd.vars)
        else:
            return n.level

    def serialize(self, filename: str):
        """Write BDDs to `filename`.

        The format can be:
        - dddmp v3: `'.dddmp'`
        - dddmp v2: `'.dddmp2'`
        - PDF: `'.pdf'`
        - PNG: `'.png'`
        - SVG: `'.svg'`
        """
        self.bdd.dump(filename=filename, roots=[self.root])
        #self.bdd.dump(filename=filename)

        if format == '.dddmp':
             # Convert to dddmp format version 3.0 (adding the '.varnames' field)
            dddmp_v2_to_v3(filename)

    def traverse(self):
        root = self.root
        self.mark = defaultdict(bool)
        self._traverse(root)

    def _traverse(self, n):
        print('-----')
        print(f'n: {n} ({n.var}) ({n.node}) ({n.level})')

        self.mark[n.node] = not self.mark[n.node]
        if not self.is_terminal(n):

            level, low, high = self.bdd.succ(n)
            print(f'|--level: {level}')
            print(f'|--low: {low} ({low.var})')
            print(f'|--high: {high} ({high.var})')
            print('-----')

            if self.mark[n.node] != self.mark[low.node]:
                self._traverse(low)
            if self.mark[n.node] != self.mark[high.node]:
                self._traverse(high)


    def is_terminal(self, node: Function) -> bool:
        return node.var is None    

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
