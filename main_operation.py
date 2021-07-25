from famapy.metamodels.fm_metamodel.operations import get_core_features, count_leaf_features, max_depth_tree

from famapy.metamodels.fm_metamodel.transformations.featureide_parser import FeatureIDEParser

from famapy.metamodels.fm_metamodel.operations.metrics import Metrics


INPUT_FMS = 'input_fms/FeatureIDE_models/'
PIZZA_FM = INPUT_FMS + 'pizzas.xml'


if __name__ == "__main__":
    fm = FeatureIDEParser(PIZZA_FM).transform() 
    core_features = get_core_features(fm)
    print([str(f) for f in core_features])

    nof_leafs = count_leaf_features(fm)
    print(f'#Leaf-features: {nof_leafs}')

    max_dt = max_depth_tree(fm)
    print(f'#Max-depth tree: {max_dt}')

    metrics = Metrics(fm)
    print(f'#Features: {metrics.nof_features()}')
    print(f'#Group-features: {metrics.nof_group_features()}')
    print(f'#Alternative-groups: {metrics.nof_alternative_groups()}')
    print(f'#Or-groups: {metrics.nof_or_groups()}')
    print(f'#Abstract features: {metrics.nof_abstract_features()}')
    print(f'#Leaf features: {metrics.nof_leaf_features()}')
    print(f'#Cross-tree constraints: {metrics.nof_cross_tree_constraints()}')


