from famapy.metamodels.fm_metamodel.models import FeatureModel, Feature

def is_mandatory(feature: Feature) -> bool:
    parent = feature.get_parent()
    if not parent:
        return True
    return any(r.is_mandatory() and r.children[0] == feature for r in parent.get_relations())

def is_optional(feature: Feature) -> bool:
    parent = feature.get_parent()
    if not parent:
        return True
    return any(r.is_optional() and r.children[0] == feature for r in parent.get_relations())

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
    features = feature_model.get_features()
    childrens = 0
    for feat in features:
        for relation in feat.get_relations():
            childrens += len(relation.children)
    return round(childrens / len(features), precision)

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