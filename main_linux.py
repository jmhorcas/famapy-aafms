from famapy.metamodels.bdd_metamodel.models.bdd_model import BDDModel
import time
import cProfile

from collections import defaultdict
from famapy.metamodels.fm_metamodel.transformations.featureide_parser import FeatureIDEParser

from famapy.metamodels.cnf_metamodel.transformations.cnf_reader import CNFReader

from famapy.metamodels.bdd_metamodel.transformations.cnf_to_bdd import CNFToBDD
from famapy.metamodels.bdd_metamodel.transformations.bdd_writer import BDDDumpFormat, BDDWriter
from famapy.metamodels.bdd_metamodel.operations import BDDProducts, BDDNumberOfConfigurations, BDDProductDistributionBF, BDDFeatureInclusionProbabilitlyBF, BDDSampling

# Models in FIDE
INPUT_FMS = 'input_fms/FeatureIDE_models/'
LINUX_FM = INPUT_FMS + 'linux-2.6.33.3.xml'

# Models in CNF
INPUT_CNFS = 'input_fms/cnf_models/'
LINUX_FM_CNF = INPUT_CNFS + 'linux-2.6.33.3-cnf.txt'

def main():
    # Load the featuer model from the FeatureIDE format
    start_time = time.time()
    fm_model = FeatureIDEParser(LINUX_FM).transform()
    end_time = time.time()
    print(f'Time FeatureIDEParser: {end_time-start_time}s')

    # Get features
    start_time = time.time()
    features = fm_model.get_features()
    end_time = time.time()
    print(f'#Features: {len(features)}')
    print(f'Time get_features: {end_time-start_time}s')
    
    # Get constraints
    start_time = time.time()
    constraints = fm_model.get_constraints()
    end_time = time.time()
    print(f'#CTCs: {len(constraints)}')
    print(f'Time get_constraints: {end_time-start_time}s')

    # Load the CNF model from a CNF formula
    start_time = time.time()
    cnf_model = CNFReader(LINUX_FM_CNF).transform()
    end_time = time.time()
    print(f'Time CNFReader: {end_time-start_time}s')
    print(f'CNF notation: {cnf_model.get_cnf_notation()}')
    print(f'CNF formula: {cnf_model.get_cnf_formula(BDDModel.CNF_NOTATION)[0:100]}')
    
    # Create the BDD model from the CNF model
    start_time = time.time()
    bdd_model = CNFToBDD(cnf_model).transform()
    end_time = time.time()
    print(f'Time CNFToBDD: {end_time-start_time}s')

    # Save the BDD as a .png
    # bdd_writer = BDDWriter(bdd_model.root.var+'.png', bdd_model)
    # bdd_writer.set_format(BDDDumpFormat.PNG)
    # bdd_writer.set_roots([bdd_model.root])
    # bdd_writer.transform()

    # # BDD Solutions operation
    # solutions = BDDProducts().execute(bdd_model).get_result()
    # for i, sol in enumerate(solutions):
    #     print(f'Sol. {i}: {[f for f in sol.elements if sol.elements[f]]}')
    raise
    # BDD number of solutions
    nof_solutions = BDDNumberOfConfigurations().execute(bdd_model).get_result()
    print(f'#Solutions: {nof_solutions}')

    # # BDD Sampling
    # sample = BDDSampling(size=5, with_replacement=False).execute(bdd_model).get_result()
    # print('Uniform Random Sampling:')
    # for i, sol in enumerate(sample):
    #     print(f'Sol. {i}: {[f for f in sol.elements if sol.elements[f]]}')

if __name__ == "__main__":
    main()
    #cProfile.run('main()')
