import copy

from famapy.core.models import Configuration

from famapy.metamodels.fm_metamodel.models.feature_model import Feature


class FMConfiguration(Configuration):

    def __init__(self, elements: dict = {}):
        super().__init__(elements)

    def add_feature(self, feature: Feature, selected: bool=True):
        self.elements[feature] = selected

    def is_selected(self, feature: Feature) -> bool:
        return feature in self.elements and self.elements[feature]

    def get_selected_features(self) -> set:
        return {f for f in self.elements.keys() if self.elements[f]}

    def clone(self) -> 'FMConfiguration':
        return FMConfiguration(copy.copy(self.elements))

    def __eq__(self, other: 'FMConfiguration') -> bool:
        return self.elements == other.elements

    def __hash__(self) -> int:
        return hash(frozenset(self.elements.items()))

    def __len__(self):
        return len(self.get_selected_features())

    def __str__(self) -> str:
        return str([str(e) for e in self.elements.keys() if self.elements[e]])

