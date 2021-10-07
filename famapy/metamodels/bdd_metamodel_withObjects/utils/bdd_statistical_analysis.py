import math
import random
import itertools
from collections import defaultdict
from typing import TYPE_CHECKING

from famapy.metamodels.fm_metamodel.models.fm_configuration import FMConfiguration
from famapy.metamodels.fm_metamodel.models.feature_model import FeatureModel

from famapy.metamodels.bdd_metamodel.models.bdd_model import BDDModel


class BDDHelperSA:

    def __init__(self, bdd_model: BDDModel):
        self.bdd_model = bdd_model

    def product_distribution(self) -> list[int]:
        mark = defaultdict(bool)
        dist = {-1: [], 1: [1]}
        #self.bdd_model.bdd.collect_garbage()
        self.bdd_model.serialize('bdd.png', 'png')
        root = self.bdd_model.reference


        #root_var = self.bdd_model.bdd.var_at_level(0)
        #root_node = self.bdd_model.bdd.var(root_var)
        #print(f'True root: {root_node.var}')
        #print(f'False root u: {self.bdd_model.bdd.level_of_var(self.bdd_model.reference.var)}')
        #print(help(self.bdd_model.root))
        # print(self.bdd_model.variables)
        # print(f'Root: {root}')
        # print(f'Root: {self.bdd_model.root.var}')
        # print(f'Root: {self.bdd_model.bdd.var(root)}')
        # print(self.bdd_model.bdd.vars)
        #root_node = self.bdd_model.reference
        solutions = self.bdd_model.bdd.count(root, nvars=len(self.bdd_model.variables))
        print(f'Solutions: {solutions}')
        self.get_prod_dist(root, mark, dist)
        return dist[root.node]

    def var(self, n) -> int:
        """Position of the variable that labels the node n in the ordering.
        
        Example: node `n4` is labeled `B`, and `B` is in the second position of the ordering `[A,B,C]`.
        thus var(n4) = 2.
        """
        if n.node == -1 or n.node == 1:
            return len(self.bdd_model.variables) + 1
        else:
            return n.level + 1

    def get_prod_dist(self, n, mark, dist):
        print('*****')
        print(f'node: {n.var}')
        print(f'dist: {dist}')
        print(f'mark: {mark}')
        print('*****')
        mark[n.node] = not mark[n.node]
       
        if n.var is not None:  # n is non-terminal
            # Traverse
            if mark[n.node] != mark[n.low.node]:
                self.get_prod_dist(n.low, mark, dist)
            
            # Compute low_dist to account for the removed nodes through low
            print(f'node: {n.var}')
            print(f'var(n): {self.var(n)}')
            print(f'var(n.low={n.low.var}): {self.var(n.low)}')
            removed_nodes = self.var(n.low) - self.var(n) - 1
            print(f'removed_nodes-low: {removed_nodes}')
            low_dist = [0] * (removed_nodes+len(dist[n.low.node]))
            for i in range(removed_nodes+1):
                for j in range(len(dist[n.low.node])):
                    low_dist[i+j] = low_dist[i+j] + dist[n.low.node][j] * math.comb(removed_nodes, i)

            # Traverse
            if mark[n.node] != mark[n.high.node]:
                self.get_prod_dist(n.high, mark, dist)
            
            # Compute high_dist to account for the removed nodes through high
            removed_nodes = self.var(n.high) - self.var(n) - 1
            print(f'node: {n.var}')
            print(f'var(n.high={n.low.high}): {self.var(n.high)}')
            print(f'removed_nodes-high: {removed_nodes}')
            high_dist = [0] * (removed_nodes+len(dist[n.high.node]))
            for i in range(removed_nodes+1):
                for j in range(len(dist[n.high.node])):
                    high_dist[i+j] = high_dist[i+j] + dist[n.high.node][j] * math.comb(removed_nodes, i)

            # Combine low and high distributions
            if len(low_dist) > len(high_dist):
                #dist_length = len(dist[n.low.node])
                dist_length = len(low_dist)
            else:
                #dist_length = len(dist[n.high.node]) + 1
                dist_length = len(high_dist) + 1
            dist[n.node] = [0] * dist_length

            print('==========')
            print(f'node: {n.var}')
            print(f'low_dist = {low_dist}')
            print(f'dist[n.low.node] = {dist[n.low.node]}')
            
            print(f'high_dist = {high_dist}')
            print(f'dist[n.high.node] = {dist[n.high.node]}')

            print(f'dist[n.node] = {dist[n.node]}')
            print('----------')

            for i in range(len(low_dist)):
                dist[n.node][i] = low_dist[i]
            for i in range(len(high_dist)):
                dist[n.node][i+1] = dist[n.node][i+1] + high_dist[i]

            print(f'dist[n.node] = {dist[n.node]}')
            print('==========')

    def bdd_traversing(self):
        mark = defaultdict(bool)
        print(f'BDD: {self.bdd_model.bdd}')
        print(f'vars: {self.bdd_model.bdd.vars}')
        print(f'expr: {self.bdd_model.bdd.to_expr(self.bdd_model.reference)}')
        #help(self.bdd_model.bdd)
        
        print(f'Root: {self.bdd_model.root}')
        print('------')
        for v in self.bdd_model.bdd.vars:
            print(f'Var: {v}')
            node = self.bdd_model.bdd.var(v)
            print(f'Node: {node}')
            print(f'Dag size: {node.dag_size}')
            print(f'Support: {self.bdd_model.bdd.support(node)}')
            
            #help(node)

            print('------')

        root = self.bdd_model.reference

        self.print_descendants(self.bdd_model.bdd, self.bdd_model.reference, set())

        #root_var = self.bdd_model.bdd.var_at_level(0)
        #root = self.bdd_model.bdd.var(root_var)
        #print(f'Traversing the BDD from node: {root.var}')
        #self.traverse(root, mark)

    def traverse(self, n, mark):
        print(f'-----------')
        print(f'n: {n}')
        print(f'node: {n.node}')
        print(f'level: {n.level}')
        print(f'var: {n.var}')
        print(f'low: {n.low}')
        print(f'high: {n.high}') 
        print(f'-----------')
        mark[n.node] = not mark[n.node]
        if n.var is not None:  # n is non-terminal
            if mark[n.node] != mark[n.low.node]:
                self.traverse(n.low, mark)
            if mark[n.node] != mark[n.high.node]:
                self.traverse(n.high, mark)            

    def print_descendants(self, bdd, u, visited):
        p = u.node
        i, v, w = bdd.succ(u)
        # visited ?
        if p in visited:
            return
        # remember
        visited.add(p)
        print(u)
        # u is terminal ?
        if v is None:
            return
        self.print_descendants(bdd, v, visited)
        self.print_descendants(bdd, w, visited)

    def feature_inclusion_probability(self):

        def get_node_pr(n):
            mark[n] = not mark[n] 
            if n.var is not None:  # n is non-terminal
                
                # Explore low
                if n.low.var is None:
                    p[n.low] = p[n.low] + p[n]
                else:
                    p[n.low] = p[n.low] + p[n]/2
                if mark[n] != mark[n.low]:
                    get_node_pr(n.low)
                
                # Explore high
                if n.high.var is None: 
                    p[n.high] = p[n.high] + p[n] 
                else:
                    p[n.high] = p[n.high] + p[n]/2 
                if mark[n] != mark[n.high]:
                    get_node_pr(n.high)

                 
        def get_joint_pr(n):
            mark[n] = not mark[n]
            if n.var is not None:  # n is non-terminal

                # Explore low
                if n.low.node == -1:
                    pass
        
        mark = defaultdict(bool)
        root = self.bdd_model.root
        print(f'Variable order: {self.bdd_model.variable_order}')
        print(f'Root: {root.var}')
        print(f'Root id: {root.node}')
        p = defaultdict(float)
        p[root] = 1/2
        #get_node_pr(root)
        #get_joint_pr(root)
        #p['formula'] = p[]        
