from collections import defaultdict

from famapy.metamodels.fm_metamodel.transformations.featureide_parser import FeatureIDEParser

from famapy.metamodels.cnf_metamodel.transformations.cnf_reader import CNFReader

from famapy.metamodels.bdd_metamodel.transformations.bdd_writer import BDDDumpFormat, BDDWriter
from famapy.metamodels.bdd_metamodel.transformations.cnf_to_bdd import CNFToBDD
from famapy.metamodels.bdd_metamodel.operations.fm_operations import BDDProducts, BDDNumberOfConfigurations, BDDProductDistributionBF, BDDFeatureInclusionProbabilitlyBF, BDDSampling


# Models in FeatureIDE format for testing
INPUT_FMS = 'input_fms/FeatureIDE_models/'
PIZZA_FM = INPUT_FMS + 'pizzas.xml'

# Models in CNF for testing (the same model in different CNF syntax notation)
INPUT_CNFS = 'input_fms/cnf_models/'
PIZZA_FM_CNF_SHORT = INPUT_CNFS + 'pizza_cnf_short.txt'
PIZZA_FM_CNF_JAVA = INPUT_CNFS + 'pizza_cnf_java.txt'
PIZZA_FM_CNF_LOGIC = INPUT_CNFS + 'pizza_cnf_logic.txt'
PIZZA_FM_CNF_TEXTUAL = INPUT_CNFS + 'pizza_cnf_textual.txt'
SIMPLE_EXAMPLE = INPUT_CNFS + 'pizza_cnf_short.txt'


def main():
    # Load the feature model from the FeatureIDE format
    fm = FeatureIDEParser(PIZZA_FM).transform() 

    # Load the CNF model from a CNF formula
    cnf_model = CNFReader(SIMPLE_EXAMPLE).transform()

    # Create the BDD model from the CNF model
    bdd_model = CNFToBDD(cnf_model).transform()

    # Save the BDD as a .png
    #bdd_writer = BDDWriter(bdd_model.root.var+'.png', bdd_model)
    bdd_writer = BDDWriter('mi_pizza.png', bdd_model)
    bdd_writer.set_format(BDDDumpFormat.PNG)
    bdd_writer.set_roots([bdd_model.root])
    bdd_writer.transform()

    # BDD Solutions operation
    solutions = BDDProducts(fm).execute(bdd_model).get_result()
    for i, sol in enumerate(solutions):
        print(f'Sol. {i}: {[str(f) for f in sol.elements if sol.elements[f]]}')

    # BDD number of solutions
    nof_solutions = BDDNumberOfConfigurations(fm).execute(bdd_model).get_result()
    print(f'#Solutions: {nof_solutions}')

    assert len(solutions) == nof_solutions 

    # BDD product distribution
    dist = BDDProductDistributionBF(fm).execute(bdd_model).get_result()
    print(f'Product Distribution: {dist}')

    assert sum(dist) == nof_solutions

    # BDD feature inclusion probabilities
    prob = BDDFeatureInclusionProbabilitlyBF(fm).execute(bdd_model).get_result()
    print('Feature Inclusion Probabilities:')
    for f in prob.keys():
        print(f'{f}: {prob[f]}')

    # BDD Sampling
    sample = BDDSampling(fm, size=5, with_replacement=False).execute(bdd_model).get_result()
    print('Uniform Random Sampling:')
    for i, sol in enumerate(sample):
        print(f'Sol. {i}: {[str(f) for f in sol.elements if sol.elements[f]]}')

    # # Check uniformity
    # stats = defaultdict(int)
    # N = int(1e4)
    # for i in range(N):
    #     sample = BDDSampling(fm, size=1, with_replacement=False).execute(bdd_model).get_result()
    #     for c in sample:
    #         stats[c] += 1

    # for i, c in enumerate(stats):
    #     print(f"{i}: {stats[c]/N*100}")

    from famapy.metamodels.bdd_metamodel.operations.others.product_distribution import ProductDistribution
    from famapy.metamodels.bdd_metamodel.operations.bdd_product_distribution_bf import BDDProductDistributionBF as PDist
    # Load the CNF model from a CNF formula
    cnf_model = CNFReader(SIMPLE_EXAMPLE).transform()

    # Create the BDD model from the CNF model
    bdd_model = CNFToBDD(cnf_model).transform()

    bdd_writer = BDDWriter('simple_example.png', bdd_model)
    bdd_writer.set_format(BDDDumpFormat.PNG)
    bdd_writer.set_roots([bdd_model.root])
    bdd_writer.transform()

    # BDD product distribution
    dist = PDist().execute(bdd_model).get_result()
    print(f'Product Distribution 2: {dist}')

    dist = ProductDistribution().execute(bdd_model).get_result()
    print(f'Product Distribution 3: {dist}')

if __name__ == "__main__":
    main()
