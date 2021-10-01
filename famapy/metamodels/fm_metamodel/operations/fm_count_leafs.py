from famapy.core.operations import CountLeafs

from famapy.metamodels.fm_metamodel.models import FeatureModel


class FMCountLeafs(CountLeafs):

    def __init__(self) -> None:
        self.result = 0

    def get_result(self) -> int:
        return self.result

    def execute(self, model: FeatureModel) -> 'FMCountLeafs':
        self.result = count_leaf_features(model)
        return self

    def get_number_of_leafs(self) -> int:
        return self.get_result()


def count_leaf_features(feature_model: FeatureModel) -> int:
    return sum(len(f.get_relations()) == 0 for f in feature_model.get_features())
