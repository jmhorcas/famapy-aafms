from collections import defaultdict

from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser

from famapy.metamodels.cnf_metamodel.transformations.cnf_reader import CNFReader

from famapy.metamodels.bdd_metamodel.transformations.bdd_writer import BDDDumpFormat, BDDWriter
from famapy.metamodels.bdd_metamodel.transformations.cnf_to_bdd import CNFToBDD
from famapy.metamodels.bdd_metamodel.operations.fm_operations import BDDProducts, BDDNumberOfConfigurations, BDDProductDistributionBF, BDDFeatureInclusionProbabilitlyBF, BDDSampling
from famapy.metamodels.pysat_metamodel.transformations.fm_to_pysat import FmToPysat
from famapy.metamodels.cnf_metamodel.transformations.pysat_to_cnf import PysatToCNF

# Models in FeatureIDE format for testing
INPUT_FMS = 'input_fms/FeatureIDE_models/'
PIZZA_FM = INPUT_FMS + 'pizzas.xml'

# Models in CNF for testing (the same model in different CNF syntax notation)
INPUT_CNFS = 'input_fms/cnf_models/'
PIZZA_FM_CNF_SHORT = INPUT_CNFS + 'pizza_cnf_short.txt'
PIZZA_FM_CNF_JAVA = INPUT_CNFS + 'pizza_cnf_java.txt'
PIZZA_FM_CNF_LOGIC = INPUT_CNFS + 'pizza_cnf_logic.txt'
PIZZA_FM_CNF_TEXTUAL = INPUT_CNFS + 'pizza_cnf_textual.txt'
SIMPLE_EXAMPLE = INPUT_CNFS + 'simple_example.txt'


def main():
    # Load the feature model from the FeatureIDE format
    fm = FeatureIDEParser(PIZZA_FM).transform() 

    pysat_model = FmToPysat(fm).transform()
    cnf_model = PysatToCNF(pysat_model).transform()
    bdd_model = CNFToBDD(cnf_model).transform()

    # BDD product distribution
    dist = BDDProductDistributionBF(fm).execute(bdd_model).get_result()
    print(f'Product Distribution: {dist}')

    import numpy as np
    import matplotlib.pyplot as plt

    # Create data
    x = range(len(fm.get_features())+1)
    y = dist

    # Area plot
    plt.title("Product distribution")
    plt.xlabel("#Features")
    plt.ylabel("#Products")

    plt.plot(x, y, color='black')
    plt.fill_between(x, y, color='grey')
    plt.legend(loc="best")
    plt.show()

    # print(cnf_model.get_cnf_formula())
    # print("--------------------------")
    # print(pysat_model.cnf.clauses)
    # print(pysat_model.features)
    # cnf_formula = []
    # for c in pysat_model.cnf.clauses:
    #     cnf_formula.append(list(map(lambda l: 'Not ' + pysat_model.features[abs(l)] if l < 0 else pysat_model.features[abs(l)], c)))
    # print(cnf_formula)


if __name__ == "__main__":
    main()
