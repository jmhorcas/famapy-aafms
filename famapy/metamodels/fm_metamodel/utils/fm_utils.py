from famapy.metamodels.fm_metamodel.models import FeatureModel, Feature


def is_mandatory(feature: Feature) -> bool:
    """A feature is mandatory if it is the root or its parent has a mandatory relation with the feature."""
    return feature.get_parent() is None or any(r.is_mandatory() and r.children[0] == feature for r in feature.get_parent().get_relations())

def is_optional(feature: Feature) -> bool:
    """A feature is optional if it is not the root and its parent has an optional relation with the feature."""
    return feature.get_parent() is not None and any(r.is_optional() and r.children[0] == feature for r in feature.get_parent().get_relations())

def is_or_group(feature: Feature) -> bool:
    return any(r.is_or() for r in feature.get_relations())

def is_alternative_group(feature: Feature) -> bool:
    return any(r.is_alternative() for r in feature.get_relations())

def is_group(feature: Feature) -> bool:
    return is_or_group(feature) or is_alternative_group(feature)

def select_parent_features(feature: Feature) -> list[Feature]:
    features = []
    parent = feature.get_parent()
    while parent:
        features.append(parent)
        parent = parent.get_parent()
    return features

def average_branching_factor(feature_model: FeatureModel, precision: int=2) -> float:
    nof_branches = 0
    nof_children = 0
    for feature in feature_model.get_features():
        if feature.get_relations():
            nof_branches += 1
            nof_children += sum(len(r.children) for r in feature.get_relations())
    return round(nof_children / nof_branches, precision)

    # nof_childrens = sum(sum(len(r.children) for r in f.get_relations()) for f in feature_model.get_features())
    # return round(nof_childrens / len(feature_model.get_features()), precision)

def max_depth_tree(feature_model: FeatureModel) -> int:
    return max(len(select_parent_features(f)) for f in leaf_features(feature_model))

def core_features(feature_model: FeatureModel) -> list[Feature]:
    if not feature_model.root:
        return []

    core_features = [feature_model.root]
    features = [feature_model.root]
    while features:
        feature = features.pop()
        for relation in feature.get_relations():
            if relation.is_mandatory():
                core_features.extend(relation.children)
                features.extend(relation.children)
    return core_features

def leaf_features(feature_model: FeatureModel) -> list[Feature]:
    return [f for f in feature_model.get_features() if len(f.get_relations()) == 0]

def count_leaf_features(feature_model: FeatureModel) -> int:
    return sum(len(f.get_relations()) == 0 for f in feature_model.get_features())

