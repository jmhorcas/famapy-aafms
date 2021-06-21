from famapy.metamodels.bdd_metamodel.utils.bdd_helper import BDDHelper
from famapy.metamodels.bdd_metamodel.transformations.cnf_to_bdd import CNFToBDD
from famapy.metamodels.pysat_metamodel.transformations.cnf_to_pysat import CNFToPysat
from famapy.metamodels.pysat_metamodel.utils.aafms_helper import AAFMsHelper

from famapy.metamodels.cnf_metamodel.models.cnf_model import CNFNotation
from famapy.metamodels.cnf_metamodel.transformations.cnf_reader import CNFReader
from famapy.metamodels.cnf_metamodel.transformations.cnf_writer import CNFWriter

from famapy.metamodels.pysat_metamodel.operations.glucose3_products import Glucose3Products

#from sampling.bdd_sampler_uned import BDDSamplerUNED
#from sampling.fm_pysat_sampler import FMPySATSampling

from famapy.metamodels.fm_metamodel.models.fm_configuration import FMConfiguration
from famapy.metamodels.fm_metamodel.transformations.featureide_parser import FeatureIDEParser
from famapy.metamodels.fm_metamodel.utils import fm_utils

from famapy.metamodels.pysat_metamodel.utils.aafms_helper import AAFMsHelper

#from famapy.metamodels.bdd_metamodel.utils.bdd_helper import BDDHelper

from famapy.metamodels.pysat_metamodel.transformations.fm_to_pysat import FmToPysat

from famapy.metamodels.bdd_metamodel.operations.product_distribution import ProductDistribution
from famapy.metamodels.bdd_metamodel.operations import BDDProductDistributionBF, BDDFeatureInclusionProbabilitlyBF, BDDNumberOfConfigurations

from famapy.metamodels.bdd_metamodel.utils.bdd_sampler import BDDSampler 


INPUT_FMS = 'input_fms/FeatureIDE_models/'
INPUT_CNFS = 'input_fms/cnf_models/'
PIZZA_FM = INPUT_FMS + 'pizzas.xml'
PIZZA_NOCTCS_FM = INPUT_FMS + 'pizzas_noCTCs.xml'
JHIPSTER_FM = INPUT_FMS + 'jHipster.xml'
WEAFQAS_FM = INPUT_FMS + 'WeaFQAs.xml'
PIZZA_FM_CNF_SHORT = INPUT_CNFS + 'pizza_cnf_short.txt'
PIZZA_FM_CNF_JAVA = INPUT_CNFS + 'pizza_cnf_java.txt'
PIZZA_FM_CNF_LOGIC = INPUT_CNFS + 'pizza_cnf_logic.txt'
PIZZA_FM_CNF_TEXTUAL = INPUT_CNFS + 'pizza_cnf_textual.txt'
BDD_TEST_FM = INPUT_FMS + 'bdd_test.xml'
BDD_TEST_CNF = INPUT_CNFS + 'bdd_test_cnf.txt'


def main():
    fm = FeatureIDEParser(BDD_TEST_FM).transform() 
    cnf_model = CNFReader(BDD_TEST_CNF).transform()
    bdd_model = CNFToBDD(cnf_model).transform()

    bdd_helper = BDDHelper(fm, bdd_model)

    print(f'BDD: {bdd_model.bdd}')
    print(f'Variable order: {bdd_model.bdd.vars}')  # dict 'var' -> level
    print(f'#BDD nodes: {len(bdd_model.bdd)}')
    print(f'Reference node: {bdd_model.reference}')
    print(f'Reference var: {bdd_model.reference.var}')
    print(f'Reference level: {bdd_model.reference.level}')

    path = 'bdd.png'
    print(f'BDD serialized in: {path}')
    bdd_model.serialize(path, 'png')

    #help(bdd_model.bdd)

    print(f'Enumerating configs:')
    configs = bdd_helper.get_configurations()
    for i, c in enumerate(configs):
        print(f'{i}: {c}')
    print(f'len(configs): {len(configs)}')
    print(f'#configs:: {bdd_helper.get_number_of_configurations()}')
    
    print(f'Computing product distribution:')
    pd = ProductDistribution().execute(bdd_model)
    dist = pd.get_result()
    print(f'PD: {dist}')

def bdd_orderings():
    fm = FeatureIDEParser(BDD_TEST_FM).transform() 
    cnf_model = CNFReader(BDD_TEST_CNF).transform()
    bdd_model = CNFToBDD(cnf_model).transform()

    bdd_helper = BDDHelper(fm, bdd_model)
    print(f'BDD: {bdd_model.bdd}')
    vars = bdd_model.bdd.vars 
    print(f'Original order: {vars}')  # dict 'var' -> level

    import itertools
    for order in itertools.permutations(vars):
        new_variable_order = {v: vars[v] for v in order}
        print(f'New variable order: {new_variable_order}') 
        bdd_model.bdd.reorder(new_variable_order)
        print(f'Variable order: {bdd_model.bdd.vars}')
        print(f'#BDD nodes: {len(bdd_model.bdd)}')
        print(f'Counts: {bdd_helper.get_number_of_configurations()}')


def main_bdd_sampler():
    fm = FeatureIDEParser(PIZZA_FM).transform() 
    cnf_model = CNFReader(PIZZA_FM_CNF_JAVA).transform()
    bdd_model = CNFToBDD(cnf_model).transform()

    print(bdd_model.bdd.levels)
    
    
    bdd_sampler = BDDSampler(fm, bdd_model)


    #prob = bdd_sampler.get_all_node_probabilities()
    #print(prob)
    print(f'Vars: {bdd_model.bdd.vars}')

    p_config = {'Pizza': True, 'Big': True}
    elements = {fm.get_feature_by_name(f): s for f, s in p_config.items()}
    fm_config = FMConfiguration(elements)

    sample = set()
    for i in range(100):
        config = bdd_sampler.generate_random_configuration()
        sample.add(config)
    
    #print(f'Config: {config}')
    print(f'#configs: {len(sample)}')

def bdd_traverse():
    fm = FeatureIDEParser(PIZZA_FM).transform() 
    cnf_model = CNFReader(PIZZA_FM_CNF_LOGIC).transform()
    bdd_model = CNFToBDD(cnf_model).transform()

    bdd_model.traverse()

    #bdd_model.serialize('bdd.png')
    print(f'CNF: {bdd_model.cnf_formula}')

    # root = bdd_model.root 
    # print(root.negated)
    # v = ~root 
    # print(v.negated)
    # bdd_model.bdd.collect_garbage()
    # bdd_model.bdd.dump('v.png', roots=[v])

    # print(f'root: {root} (var={root.var}), (level={root.level}), (id={root.node}), (negated={root.negated})')
    # print(f'root.low: {root.low} (var={root.low.var}), (level={root.low.level}), (id={root.low.node}), (negated={root.low.negated})')
    # print(f'root.high: {root.high} (var={root.high.var}), (level={root.high.level}), (id={root.high.node}), (negated={root.high.negated})')
    
    # level, low, high = bdd_model.bdd.succ(root)
    # print(f'-----level: {level}')
    # print(f'root: {root} (var={root.var}), (level={root.level}), (id={root.node}), (negated={root.negated})')
    # print(f'low: {low} (var={low.var}), (level={low.level}), (id={low.node}), (negated={low.negated})')
    # print(f'high: {high} (var={high.var}), (level={high.level}), (id={high.node}), (negated={high.negated})')

    print(f'Computing product distribution:')
    pd = ProductDistribution().execute(bdd_model)
    dist = pd.get_result()
    print(f'PD: {dist}')

def bdd_product_distribution():
    fm = FeatureIDEParser(PIZZA_FM).transform() 
    cnf_model = CNFReader(PIZZA_FM_CNF_LOGIC).transform()
    bdd_model = CNFToBDD(cnf_model).transform()

    p_config = {'Pizza': True, 'Big': True}
    elements = {fm.get_feature_by_name(f): s for f, s in p_config.items()}
    fm_config = FMConfiguration(elements)

    dist = BDDProductDistributionBF(bdd_model, fm_config).execute(fm).get_result()
    print(f'Dist: {dist}')
    print(f'#Products: {sum(dist)}')

    prob = BDDFeatureInclusionProbabilitlyBF(bdd_model, fm_config).execute(fm).get_result()
    for f in prob.keys():
        print(f'{f}: {prob[f]}')
    print(f'#Configs: {BDDNumberOfConfigurations(bdd_model).execute(fm).get_result()}')

if __name__ == "__main__":
    #main()
    #main_bdd_sampler()
    #bdd_orderings()
    #bdd_traverse()
    bdd_product_distribution()
