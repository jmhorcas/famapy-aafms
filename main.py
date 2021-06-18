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
    ########## CNF ##########
    cnf_reader = CNFReader(PIZZA_FM_CNF_LOGIC)
    cnf_model = cnf_reader.transform()
    print(f"CNF features: {cnf_model.features}")
    print(f"CNF vars: {cnf_model.variables}")
    print(f"CNF clauses: {cnf_model.cnf.clauses}")
    cnf_formula = cnf_reader.get_cnf_formula(cnf_output_syntax=CNFNotation.JAVA)
    print(f"CNF formula: {cnf_formula}")


    ########## Products operation ##########
    product_op = Glucose3Products()
    product_op.execute(cnf_model)
    products = product_op.get_products()
    for i, p in enumerate(products):
        print(f"P({i}): {p}")
    print(f"#Products: {len(products)}")


    ########## BDD ##########
    try:
        from dd.cudd import BDD
    except ImportError:
        from dd.autoref import BDD
    #from dd.cudd import BDD

    # BDD manager
    bdd = BDD()
    
    # Declare variables
    for v in cnf_model.variables.keys():
        bdd.declare(v)

    expression = bdd.add_expr(cnf_formula)
    nof_configurations = bdd.count(expression, nvars=len(cnf_model.variables))

    print(f"#BDD Configs: {nof_configurations}")

    bdd.dump(filename='mybdd.dddmp', roots=[expression], filetype='.p')


    ########## UNED SAMPLER ##########
    import subprocess
    import sys
    import os

    if 'LD_LIBRARY_PATH' not in os.environ:
        os.environ['LD_LIBRARY_PATH'] = 'lib'
    
    sample_size = 2
    bdd_dump_file = 'mybdd.dddmp'
    #subprocess.run(['export', 'LD_LIBRARY_PATH="$LD_LIBRARY_PATH:lib"'], capture_output=True, cwd='BDDSampler/',shell=True)
    command = subprocess.run(['bin/BDDSampler', '-names', str(sample_size), bdd_dump_file], capture_output=True, cwd='BDDSampler/')
    print(command.stdout)

    #sys.stdout.buffer.write(command.stdout)
    #sys.stderr.buffer.write(command.stderr)
    # sys.exit(command.returncode)

def main2():
    fide_parser = FeatureIDEParser(PIZZA_FM)
    fm = fide_parser.transform()

    sampler = BDDSamplerUNED(fm)
    sampler.fromCNF(PIZZA_FM_CNF_LOGIC)
    configurations = sampler.sample(5)
    for c in configurations:
        print(c)

    print(f"#Configs: {len(configurations)}")
    print(f"#Configs (no-rep): {len(set(configurations))}")

    stats = defaultdict(int)
    N = int(1e3)
    for i in range(N):
        configurations = sampler.sample(1)
        for c in configurations:
            stats[c] += 1

    for c in stats:
        print(f"{c}: {stats[c]}")

    stats = defaultdict(int)
    M = 10
    configurations = sampler.sample(M)
    for c in configurations:
        stats[c] += 1

    for c in stats:
        print(f"{c}: {stats[c]}")
        
    sampler.delete()

def main3():
    fide_parser = FeatureIDEParser(PIZZA_FM, no_read_constraints=True)
    fm = fide_parser.transform()

    sampler = FMPySATSampling(fm)
    sampler.fromCNF(PIZZA_FM_CNF_JAVA)
    configurations = sampler.sample(5)
    for c in configurations:
        print(c)

    stats = defaultdict(int)
    N = int(1e4)
    for i in range(N):
        configurations = sampler.sample(1)
        for c in configurations:
            stats[c] += 1

    for i, c in enumerate(stats):
        print(f"{i}: {stats[c]/N*100}")


def main4():
    fide_parser = FeatureIDEParser(PIZZA_FM, no_read_constraints=True)
    fm = fide_parser.transform()

    cnf_reader = CNFReader(PIZZA_FM_CNF_LOGIC)
    cnf_model = cnf_reader.transform()
    cnf_formula = cnf_reader.get_cnf_formula(cnf_output_syntax=CNFNotation.JAVA)

    bdd_helper = BDDHelper(feature_model=fm, cnf_filepath=PIZZA_FM_CNF_LOGIC)
    # configs = bdd_helper.get_configurations()
    # configs = set(configs)
    # for i, c in enumerate(configs):
    #     print(f'{i}: {c}')

    # print(f'#Configs: {bdd_helper.get_number_of_configurations()}')

    p_config = {'Pizza': True, 'Big': True}
    elements = {fm.get_feature_by_name(f): s for f, s in p_config.items()}
    # configs = bdd_helper.get_configurations(partial_configuration=FMConfiguration(elements))
    # configs = set(configs)
    # for i, c in enumerate(configs):
    #     print(f'{i}: {c}')
    print(f'#Configs2: {bdd_helper.get_number_of_configurations(partial_configuration=FMConfiguration(elements))}')
    print(f'#Configs2: {bdd_helper.get_number_of_configurations(partial_configuration=FMConfiguration(elements))}')
    print(f'#Configs2: {bdd_helper.get_number_of_configurations(partial_configuration=FMConfiguration(elements))}')

def main_fide():
    fm = FeatureIDEParser(PIZZA_NOCTCS_FM).transform()
    pysat_model = FmToPysat(fm).transform()
    print(f'Variables: {pysat_model.variables}')
    print(f'CNF: {pysat_model.cnf}')


    print('==========Metrics==========')
    print(f'#Features: {len(fm.get_features())}')
    print(f'#Constraints: {len(fm.get_constraints())}')
    print(f'Root: {fm.root}')
    print(f'#Abstract features: {sum(f.is_abstract for f in fm.get_features())}')
    print(f'#Mandatory features: {sum(fm_utils.is_mandatory(f) for f in fm.get_features())}')
    print(f'#Optional features: {sum(fm_utils.is_optional(f) for f in fm.get_features())}')
    print(f'#Groups: {sum(fm_utils.is_group(f) for f in fm.get_features())}')
    print(f'#Alternative-groups: {sum(fm_utils.is_alternative_group(f) for f in fm.get_features())}')
    print(f'#Or-groups: {sum(fm_utils.is_or_group(f) for f in fm.get_features())}')
    print(f'#Core features: {len(fm_utils.core_features(fm))}')
    print(f'#Leaf features: {len(fm_utils.leaf_features(fm))}')
    #print(f'#Leaf features:: {fm_utils.count_leaf_features(fm)}')
    print(f'Branching factor: {fm_utils.average_branching_factor(fm)}')
    print(f'Max depth tree: {fm_utils.max_depth_tree(fm)}')
    
def main_cnf():
    fm = FeatureIDEParser(PIZZA_FM).transform() 

    cnf_model = CNFReader(PIZZA_FM_CNF_JAVA).transform()
    print(f'CNF notation: {cnf_model.get_cnf_notation()}')
    print(f'CNF formula: {cnf_model.get_cnf_formula(cnf_model.get_cnf_notation())}')
    print(f'Features: {cnf_model.get_variables()}')

    cnf_writer = CNFWriter('prueba.txt', cnf_model)
    cnf_writer.set_notation(CNFNotation.SHORT)
    cnf_writer.transform()

    bdd_model = CNFToBDD(cnf_model).transform()
    bdd_helper = BDDHelper(fm, bdd_model)
    
    configs = bdd_helper.get_configurations()
    print(f'#Configs: {len(configs)}')

    p_config = {'Pizza': True, 'Normal': True}
    elements = {fm.get_feature_by_name(f): s for f, s in p_config.items()}
    fm_config = FMConfiguration(elements)
    configs = bdd_helper.get_configurations(fm_config)
    print(f'#Configs: {len(configs)}')

    configs = bdd_helper.get_configurations()
    print(f'#Configs: {len(configs)}')

    p_config = {'Pizza': True, 'Big': True}
    elements = {fm.get_feature_by_name(f): s for f, s in p_config.items()}
    fm_config = FMConfiguration(elements)
    configs = bdd_helper.get_configurations(fm_config)
    print(f'#Configs: {len(configs)}')

def main_bdd():
    fm = FeatureIDEParser(PIZZA_FM).transform() 
    cnf_model = CNFReader(PIZZA_FM_CNF_JAVA).transform()
    bdd_model = CNFToBDD(cnf_model).transform()

    bdd_helper = BDDHelper(fm, bdd_model)

    print(f'Root: {bdd_model.root}')
    print(f'node: {bdd_model.root.node}')
    print(f'bdd: {bdd_model.root.bdd}')
    print(f'manager: {bdd_model.root.manager}')
    print(f'level: {bdd_model.root.level}')
    print(f'len: {len(bdd_model.root)}')
    print(f'to_expr: {bdd_model.root.to_expr()}')
    print(f'high: {bdd_model.root.high}')
    print(f'low: {bdd_model.root.low}')
    print(f'ref: {bdd_model.root.ref}')
    print(f'count: {bdd_model.root.count()}')
    print(f'count all: {bdd_model.root.count(nvars=len(bdd_model.variables))}')

    print(f'variable order: {bdd_model.variable_order}')
    print(f'root variable: {bdd_model.variable_order[bdd_model.root.level]}')

    values = {bdd_model.variable_order[bdd_model.root.level] : True}
    v = bdd_model.bdd.let(values, bdd_model.root)
    print(f'#Count: {v.count()}')
    print(f'#Count all: {v.count(nvars=len(bdd_model.variables)-len(values))}')


    p_config = {'Pizza': True, 'Big': True}
    elements = {fm.get_feature_by_name(f): s for f, s in p_config.items()}
    fm_config = FMConfiguration(elements)

    configs = bdd_helper.get_configurations(fm_config)
    configs = set(configs)
    for i, c in enumerate(configs):
        print(f'{i}: {c}')
    print(f'#configs: {len(configs)}')
    #help(bdd_model.root)

    nof_configs = bdd_helper.get_number_of_configurations()
    print(f'#configs: {nof_configs}')

    nof_configs = bdd_helper.get_number_of_configurations(fm_config)
    print(f'#configs: {nof_configs}')

    # Sampling
    sample = bdd_helper.get_random_sample_uned(size=10)
    for i, c in enumerate(sample):
        print(f'{i}: {c}')
    print(f'#configs: {len(sample)}')

    ########## Checking uniformity ##########
    # stats = defaultdict(int)
    # N = int(1e4)
    # for i in range(N):
    #     configurations = bdd_helper.get_random_sample_uned(size=1)
    #     for c in configurations:
    #         stats[c] += 1

    # for i, c in enumerate(stats):
    #     print(f"{i}: {stats[c]/N*100}")

def main_product_distribution():
    fm = FeatureIDEParser(PIZZA_FM).transform() 
    cnf_model = CNFReader(PIZZA_FM_CNF_JAVA).transform()
    bdd_model = CNFToBDD(cnf_model).transform()

    bdd_helper = BDDHelper(fm, bdd_model)

    bdd_model.serialize('bdd.png', 'png')

    #print(f'Variable order: {bdd_model.variable_order}')
    #print(f'Roots: {bdd_model.bdd.to_nx(bdd_model.reference)}')
    

    #bdd_helper.bdd_traversing()
    
    #help(bdd_model.bdd.reorder)
    #bdd_model.serialize('bdd.png', 'png')
    distribution = bdd_helper.product_distribution()
    print(f'Distribution: {distribution}')
    print(f'Variable order: {bdd_model.variable_order}')
    

if __name__ == "__main__":
    #main()
    #main2()
    #main3()
    #main4()
    #main_fide()
    #main_cnf()
    #main_bdd()
    main_product_distribution()
