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
        self.root = None
        self.variables = []

    def from_cnf(self, cnf_formula: str, variables: list[str]):
        self.cnf_formula = cnf_formula
        self.variables = variables

        # Declare variables
        for v in self.variables:
            self.bdd.declare(v)

        # Build the BDD
        self.root = self.bdd.add_expr(self.cnf_formula)
        
        # Reorder variables
        # variable_order = self.bdd.vars 
        # var = self.bdd.var_at_level(0)
        # level = self.root.level
        # variable_order[self.root.var] = 0
        # variable_order[var] = level
        # self.bdd.reorder(variable_order)

        #self.root = self.bdd.var(self.bdd.var_at_level(0))
        
    def index(self, n: Function) -> int:
        """Position of the variable that labels the node `n` in the ordering (i.e., the level).
            
        Example: node `n4` is labeled `B`, and `B` is in the second position of the ordering `[A,B,C]`.
        thus var(n4) = 2.
        """
        if n.node == -1 or n.node == 1:  # index(n0) = index(n1) = s + 1, being s the number of variables.
            return len(self.bdd.vars) + 1
        else:
            return n.level + 1

    def get_high_node(self, node: Function) -> Function:
        return ~node.high if node.negated and not self.is_terminal_node(node.high) else node.high

    def get_low_node(self, node: Function) -> Function:
        return ~node.low if node.negated and not self.is_terminal_node(node.low) else node.low

    def is_terminal_node(self, node: Function) -> bool:
        return node.var is None    

    # def traverse(self):
    #     root = self.root
    #     self.mark = defaultdict(bool)
    #     self._traverse(root)

    # def _traverse(self, n):
    #     print('-----')
    #     print(f'n: {n} (var={n.var}), (level={n.level}), (id={n.node}), (negated={n.negated})')

    #     self.mark[n.node] = not self.mark[n.node]
    #     if not self.is_terminal_node(n):

    #         #level, low, high = self.bdd.succ(n)
    #         level = n.level
    #         low = n.low #self.get_low_node(n)
    #         high = n.high #self.get_high_node(n)
    #         print(f'|--level: {level}')
    #         print(f'|--low: {low} (var={low.var}), (level={low.level}), (id={low.node}), (negated={low.negated})')
    #         print(f'|--high: {high} (var={high.var}), (level={high.level}), (id={high.node}), (negated={high.negated})')
    #         if self.is_terminal_node(low) and low.negated:
    #             print(f'negated: {~low}')
    #         print('-----')

    #         if self.mark[n.node] != self.mark[low.node]:
    #             self._traverse(low)
    #         if self.mark[n.node] != self.mark[high.node]:
    #             self._traverse(high)
