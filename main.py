from collections import defaultdict
from famapy.metamodels.pysat_metamodel.utils.aafms_helper import AAFMsHelper

from famapy.metamodels.pysat_metamodel.transformations.cnf_to_pysat import CNFReader, CNFNotation

from famapy.metamodels.pysat_metamodel.operations.glucose3_products import Glucose3Products

from sampling.bdd_sampler_uned import BDDSamplerUNED
from sampling.fm_pysat_sampler import FMPySATSampling

from famapy.metamodels.fm_metamodel.models.fm_configuration import FMConfiguration
from famapy.metamodels.fm_metamodel.transformations.featureide_parser import FeatureIDEParser
from famapy.metamodels.fm_metamodel.utils import fm_utils

from famapy.metamodels.pysat_metamodel.utils.aafms_helper import AAFMsHelper

from famapy.metamodels.bdd_metamodel.utils.bdd_helper import BDDHelper



INPUT_FMS = 'input_fms/FeatureIDE_models/'
PIZZA_FM = INPUT_FMS + 'pizza.xml'
JHIPSTER_FM = INPUT_FMS + 'jHipster.xml'
PIZZA_FM_CNF_SHORT = INPUT_FMS + 'pizza_cnf_short.txt'
PIZZA_FM_CNF_JAVA = INPUT_FMS + 'pizza_cnf_java.txt'
PIZZA_FM_CNF_LOGIC = INPUT_FMS + 'pizza_cnf_logic.txt'
PIZZA_FM_CNF_TEXTUAL = INPUT_FMS + 'pizza_cnf_textual.txt'



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
    fide_parser = FeatureIDEParser(JHIPSTER_FM)
    fm = fide_parser.transform()

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
    

if __name__ == "__main__":
    #main()
    #main2()
    #main3()
    #main4()
    main_fide()