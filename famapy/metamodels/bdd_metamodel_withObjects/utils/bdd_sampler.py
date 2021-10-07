import math
import random
import itertools
from collections import defaultdict
from typing import TYPE_CHECKING

from famapy.metamodels.fm_metamodel.models.fm_configuration import FMConfiguration
from famapy.metamodels.fm_metamodel.models.feature_model import FeatureModel

from famapy.metamodels.bdd_metamodel.models.bdd_model import BDDModel, Function


class BDDSampler:
    """Uniform Random Sampling (URS) using a Binary Decision Diagram (BDD).
    
    This sampler is based on the C implementation of the BDDSampler 
    by David Fernández-Amoros from UNED (https://github.com/davidfa71/BDDSampler).
    
    It supports samples with and without replacement.

    This is a counting-based sampling inspired in the Knuth algorithm presented in Section 7.1.4 of
    [Donald E. Knuth. 2009. The Art of Computer Programming, 
    Volume 4, Fascicle 1: Bitwise Tricks & Techniques; Binary Decision Diagrams. 
    Addison-Wesley Professional.]

    Knuth showed how to accomplish uniform random sampling by subsequently partitioning the SAT solution space on variable assignments, 
    and then counting the number of solutions of the resulting parts. 

    The original algorithm by Knuth is specified on BDDs very efficiently, 
    as the probabilities required for all the possible SAT solutions are computed just once with a single BDD traversal, 
    and then reused every time a solution is generated. Knuth’s algorithm can be also adapted to SAT technology.

    Ref.: 
     - Heradio et al. [ESE 2021]: Uniform and scalable sampling of highly configurable systems.
     - Heradio et al. [SPLC 2020]: Uniform and scalable SAT-sampling for configurable systems (https://doi.org/10.1145/3382025.3414951)
    """

    def __init__(self, feature_model: FeatureModel, bdd_model: BDDModel):
        self.feature_model = feature_model
        self.bdd_model = bdd_model

    def get_all_node_probabilities(self):
        """It decorates each non-terminal node with its probability of reaching the a solution if the associated variable is set to True."""
        self.mark = defaultdict(bool)  # boolean mark for every node being either all true or all false.
        self.pr = {}  # probability of nodes: `node id` -> `float`
        self.sol = {}
        self.get_node_pr(self.root)
        return self.pr

    def get_node_pr(self, n):
        print(f'get_node_pr for n={n}')
        self.mark[n.node] = not self.mark[n.node]

        if n.node == -1:  # terminal node 0 is reached
            self.sol[n.node] = 0
        elif n.node == 1:  # terminal node 1 is reached
            self.sol[n.node] = 1
        else:
            level, low, high = self.bdd_model.bdd.succ(n)
            # Explore low
            if self.mark[n.node] != self.mark[low.node]:
                self.get_node_pr(low)
            # Explore high
            if self.mark[n.node] != self.mark[high.node]:
                self.get_node_pr(high)
            
            # Get node probabilities
            sol_low = self.sol[low.node] * 2**(self.bdd_model.index(low) - self.bdd_model.index(n) - 1)
            sol_high = self.sol[high.node] * 2**(self.bdd_model.index(high) - self.bdd_model.index(n) - 1)
            self.sol[n.node] = sol_low + sol_high 
            self.pr[n.node] = sol_high / self.sol[n.node]

    def _generate_random_configuration(self) -> dict[str, bool]:
        """Return a random configuration."""
        sample = {}
        # Generate random values for variables corresponding to reduced ROOT predecessor nodes
        for i in range(self.bdd_model.index(self.root)):
           sample[self._get_var(i)] = random.random() < 0.5
        
        # Generate random values for the remaining variables
        trav = self.root
        level, low, high = self.bdd_model.bdd.succ(trav)
        while trav.node != 1:  # Iterate until reaching the 1-terminal node 
            ind = self.bdd_model.index(trav)
            if random.random() < self.pr[trav.node]:
                trav = high
                sample[self._get_var(ind)] = True 
            else:
                trav = low
                sample[self._get_var(ind)] = False 
            # Generate random values for variables of reduced intermediate nodes
            for i in range(ind+1, self.bdd_model.index(trav)):
                sample[self._get_var(i)] = random.random() < 0.5
        return sample

    def _get_var(self, level: int) -> str:
        return self.bdd_model.bdd.var_at_level(level)

    def _get_id(self, node: Function) -> int:
        """Return the id absolute value of the node that could be complemented."""
        return abs(node.node)


    def generate_random_configuration(self, partial_configuration: FMConfiguration=None) -> FMConfiguration:
        self.root = self.bdd_model.root
        self.pr = self.get_all_node_probabilities()
        raise Exception
        #print(f'PR: {self.pr}')
        config = self._generate_random_configuration()
        #print(config)
        #print(abs(self.root.node))
        elements = {self.feature_model.get_feature_by_name(v): selected for v, selected in config.items()}
        return FMConfiguration(elements)

       # Initialize the configurations and values for BDD nodes with already known features
        # elements = {} if partial_configuration is None else partial_configuration.elements
        # values = {f.name : selected for f, selected in elements.items()}
        
        # # Set the BDD nodes with the already known features values
        #self.root = self.bdd_model.bdd.let(values, self.bdd_model.root)
        # self.bdd_model.bdd.dump(filename='bdd.png', roots=[self.root], filetype='png')
        # self.root = self.bdd_model.root
        # self.bdd_model.bdd.dump(filename='bdd.png', roots=[self.root], filetype='png')
        # self.pr = self.get_all_node_probabilities()
        # for v in self.bdd_model.bdd.vars:
        #     n = self.bdd_model.bdd.var(v)
        #     print(f'Var: {v}, id={n.node}, level={n.level}')
        #     # if self.bdd_model.bdd.var(v).node in self.pr:
        #     #     print(f'pr({v}): {self.pr[self.bdd_model.bdd.var(v).node]}')
        # print(f'PR: {self.pr}')
        # config = self._generate_random_configuration()
        # #print(config)

    def sample(self, size: int, with_replacement: bool=False, partial_configuration: FMConfiguration=None) -> list[FMConfiguration]:
        # Initialize the configurations and values for BDD nodes with already known features
        elements = {} if partial_configuration is None else partial_configuration.elements
        values = {f.name : selected for f, selected in elements.items()}
        
        # Set the BDD nodes with the already known features values
        self.root = self.bdd_model.bdd.let(values, self.bdd_model.root)
        self.pr = self.get_all_node_probabilities()
        config = self._generate_random_configuration()
        print(config)


        nof_configs = self.get_number_of_configurations(partial_configuration)
        if size < 0 or (size > nof_configs and not with_replacement):
            raise ValueError('Sample larger than population or is negative.')

        configurations = []
        for _ in range(size):
            config = self.get_random_configuration(partial_configuration)
            configurations.append(config)
        if not with_replacement:
            configurations = list(set(configurations))
            while len(configurations) < size:
                config = self.get_random_configuration(partial_configuration)
                configurations.append(config)
        return configurations 