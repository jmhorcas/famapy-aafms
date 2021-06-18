import random 
import math
from collections import defaultdict

from famapy.core.operations.abstract_operation import Operation

from famapy.metamodels.fm_metamodel.models.fm_configuration import FMConfiguration
from famapy.metamodels.fm_metamodel.models.feature_model import FeatureModel

from famapy.metamodels.bdd_metamodel.models.bdd_model import BDDModel
from dd.autoref import Function


class ProductDistribution(Operation):
    """The Product Distribution (PD) algorithm determines the number of products having a given number of features.

    It accounts for how many products have no features, one features, two features, ..., all features.

    It uses Bryant's method to traverse the BDD in post-order.

    Ref.: Heradio2019 [SPLC] - Supporting the Statistical Analysis of Variability Models (https://doi.org/10.1109/ICSE.2019.00091)
    """

    def __init__(self) -> None:
        self.result = []
        self.bdd_model = None
    
    def execute(self, model: BDDModel) -> 'ProductDistribution':
        self.bdd_model = model
        self.result = self.product_distribution()
        return self

    def get_result(self) -> list[FMConfiguration]:
        return self.result

    def product_distribution(self) -> list[int]:
        """It accounts for how many products have no features, one features, two features, ..., all features.

        It uses Bryant's method to traverse the BDD in post-order 
        by calling the auxiliary function `get_prod_dist` with the BDD root as argument.
        From the terminals to the root, it progressively obtains the partial distributions that correspond to the subBDDs
        rooted by each node, being the final distribution placed at the root.
        """
        self.mark = defaultdict(bool)  # boolean mark for every node being either all true or all false.
        self.dist = {-1: [], 1: [1]}  # distribution vectors: `node` -> `list[int]`
        root = self.bdd_model.root
        self.get_prod_dist(root)
        print(f'self.dist: {self.dist}')
        return self.dist[root.node]        

    def get_prod_dist(self, n: Function):
        self.mark[n.node] = not self.mark[n.node]

        if not self.is_terminal(n):
            
            level, low, high = self.bdd_model.bdd.succ(n)

            # Traverse
            if self.mark[n.node] != self.mark[low.node]:
                self.get_prod_dist(low)
            
            # Compute low_dist to account for the removed nodes through low
            removed_nodes = low.level - n.level - 1
            low_dist = [0] * (removed_nodes + len(self.dist[low.node]))
            for i in range(removed_nodes+1):
                for j in range(len(self.dist[low.node])):
                    low_dist[i+j] = low_dist[i+j] + self.dist[low.node][j] * math.comb(removed_nodes, i)

            # Traverse
            if self.mark[n.node] != self.mark[high.node]:
                self.get_prod_dist(high)
            
            # Compute high_dist to account for the removed nodes through high
            removed_nodes = high.level - n.level - 1
            high_dist = [0] * (removed_nodes + len(self.dist[high.node]))
            for i in range(removed_nodes+1):
                for j in range(len(self.dist[high.node])):
                    high_dist[i+j] = high_dist[i+j] + self.dist[high.node][j] * math.comb(removed_nodes, i)

            # Combine low and high distributions
            if len(low_dist) > len(high_dist):
                #dist_length = len(self.dist[low.node])
                dist_length = len(low_dist)
            else:
                #dist_length = len(self.dist[high.node]) + 1
                dist_length = len(high_dist) + 1

            self.dist[n.node] = [0] * dist_length
            for i in range(len(low_dist)):
                self.dist[n.node][i] = low_dist[i]
            for i in range(len(high_dist)):
                self.dist[n.node][i+1] = self.dist[n.node][i+1] + high_dist[i]

    def var(self, n: Function) -> int:
        """Position of the variable that labels the node n in the ordering.
            
        Example: node `n4` is labeled `B`, and `B` is in the second position of the ordering `[A,B,C]`.
        thus var(n4) = 2.
        """
        if n.node == -1 or n.node == 1:  # var(n0) = var(n1) = s + 1, being s the number of variables.
            return len(self.bdd_model.variables)
        else:
            return n.level

    def is_terminal(self, n: Function) -> bool:
        return n.var is None
    