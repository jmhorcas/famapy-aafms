import json

from famapy.core.transformations import ModelToText
from famapy.metamodels.fm_metamodel.models.feature_model import Feature, FeatureModel, Relation


class JsonWriter(ModelToText):

    @staticmethod
    def get_destination_extension() -> str:
        return 'json'

    def __init__(self, source_model: FeatureModel, path: str):
        self.path = path
        self.model = source_model

    def transform(self):
        data = {}
        root = self.model.root

        data['hierachy'] = self.process_feature(root)
        data['ctc'] = self.process_constraints()

        with open(self.path, 'w') as outfile:
            json.dump(data, outfile)
        return self.path

    def process_feature(self, feature: Feature):
        _dict = {}
        _dict["featureName"] = feature.name
        relationships = []
        for relation in feature.get_relations():
            relationships.append(self.process_relation(relation))
        _dict["relationships"] = relationships
        return _dict

    def process_relation(self, relation: Relation):
        _dict = {}
        _dict["card_min"] = relation.card_min
        _dict["card_max"] = relation.card_max

        for child in relation.children:
            _dict[child.name] = self.process_feature(child)

        return _dict

    def process_constraints(self):
        constraints = []
        for constraint in self.model.ctcs:
            _ctc = {}
            _ctc["name"] = constraint.name
            _ctc["origin"] = constraint.ast.get_childs(constraint.ast.get_root())[0].get_name()
            _ctc["destination"] = constraint.ast.get_childs(
                constraint.ast.get_root()
            )[0].get_name()
            _ctc["ctctype"] = constraint.ast.get_root().get_name()
            constraints.append(_ctc)

        return constraints
