import os 
import subprocess

from famapy.metamodels.fm_metamodel.models.fm_configuration import FMConfiguration
from famapy.metamodels.fm_metamodel.models.feature_model import FeatureModel

from famapy.metamodels.pysat_metamodel.transformations.cnf_to_pysat import CNFReader, CNFNotation

from sampling.fm_sampling import FMSampling 

try:
    from dd.cudd import BDD
except ImportError:
    from dd.autoref import BDD


def dddmp_v2_to_v3(filepath: str):
    """
    Convert the file with the BDD dump in format dddmp version 2 to version 3.

    The difference between versions 2.0 and 3.0 is the addition of the '.varnames' field.
    """

    with open(filepath, 'r') as file:
        lines = file.readlines()
        # Change version from 2.0 to 3.0
        i, line = next((i,l) for i, l in enumerate(lines) if '.ver DDDMP-2.0' in l)
        lines[i] = line.replace('2.0', '3.0')

        # Add '.varnames' field
        i, line = next((i,l) for i, l in enumerate(lines) if '.orderedvarnames' in l)
        lines.insert(i-1, line.replace('.orderedvarnames', '.varnames'))

    with open(filepath, 'w') as file:
        file.writelines(lines)
        

class BDDSamplerUNED(FMSampling):
    """Uniform Random Sampling using a BDD.
    
    This is a wrapper of the BDDSampler (implemented in c) by David Fernandez-Amoros and Rubén Heradio from UNED.
    Ref.: https://github.com/davidfa71/BDDSampler
    """

    BDDSAMPLER_DIR = 'BDDSampler/'
    BDDSAMPLER_EXE = 'bin/BDDSampler'

    def __init__(self, feature_model: FeatureModel):
        self.feature_model = feature_model
        self._bdd_dumpfile_name = self.feature_model.root.name + '.dddmp'

    def fromCNF(self, cnf_model_filepath: str):
        # Read the feature model given as a CNF formula
        cnf_reader = CNFReader(cnf_model_filepath)
        cnf_model = cnf_reader.transform()
        cnf_formula = cnf_reader.get_cnf_formula(cnf_output_syntax=CNFNotation.JAVA)

        # BDD manager
        bdd = BDD()

        # Declare variables
        for v in cnf_model.variables.keys():
            bdd.declare(v)

        # Build the BDD
        root = bdd.add_expr(cnf_formula)

        # Dump the BDD to file (dddmp format version 2.0)
        bdd.dump(filename=BDDSamplerUNED.BDDSAMPLER_DIR + self._bdd_dumpfile_name, roots=[root], filetype='.p')
        
        # Convert to dddmp format version 3.0 (adding the '.varnames' field)
        dddmp_v2_to_v3(BDDSamplerUNED.BDDSAMPLER_DIR + self._bdd_dumpfile_name)

        # Add the lib dir to LD_LIBRARY_PATH
        if 'LD_LIBRARY_PATH' not in os.environ:
            os.environ['LD_LIBRARY_PATH'] = 'lib'

        # Store the BDD and the variable order
        self.bdd = bdd
        self.variable_order = {bdd.level_of_var(var): var for var in cnf_model.variables.keys()}

    def delete(self):
        """Delete temporal files and free memory for BDD."""
        del self.bdd 
        if os.path.exists(BDDSamplerUNED.BDDSAMPLER_DIR + self._bdd_dumpfile_name):
            os.remove(BDDSamplerUNED.BDDSAMPLER_DIR + self._bdd_dumpfile_name)

    def sample(self, size: int, with_replacement: bool=False) -> list[FMConfiguration]:
        # Execute the BDDSampler @ UNED
        if with_replacement:
            command = subprocess.run([BDDSamplerUNED.BDDSAMPLER_EXE, str(size), self._bdd_dumpfile_name], capture_output=True, cwd=BDDSamplerUNED.BDDSAMPLER_DIR)
        else:
            command = subprocess.run([BDDSamplerUNED.BDDSAMPLER_EXE, '-norep', str(size), self._bdd_dumpfile_name], capture_output=True, cwd=BDDSamplerUNED.BDDSAMPLER_DIR)
        result = command.stdout
        
        # Parse the results
        configurations = list()
        binary_configurations = result.splitlines()
        for bin_config in binary_configurations:
            features_config = {self.feature_model.get_feature_by_name(self.variable_order[i]): bool(int(feature)) for i, feature in enumerate(bin_config.split())}
            configurations.append(FMConfiguration(elements=features_config))
        return configurations

