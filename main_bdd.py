from collections import defaultdict
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


    

if __name__ == "__main__":
    main()
    #bdd_orderings()
