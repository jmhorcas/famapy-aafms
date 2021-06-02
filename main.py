from collections import defaultdict
from famapy.metamodels.pysat_metamodel.utils.aafms_helper import AAFMsHelper

from famapy.metamodels.pysat_metamodel.transformations.cnf_to_pysat import CNFReader, CNFNotation

from famapy.metamodels.pysat_metamodel.operations.glucose3_products import Glucose3Products

from sampling.bdd_sampler_uned import BDDSamplerUNED
from sampling.fm_pysat_sampler import FMPySATSampling

from famapy.metamodels.fm_metamodel.transformations.featureide_parser import FeatureIDEParser

from famapy.metamodels.pysat_metamodel.utils.aafms_helper import AAFMsHelper

INPUT_FMS = 'input_fms/'
PIZZA_FM = INPUT_FMS + 'pizza.xml'
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



if __name__ == "__main__":
    #main()
    main2()
    #main3()