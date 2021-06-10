import xml.etree.ElementTree as ET

from famapy.core.models.ast import AST
from famapy.core.transformations import TextToModel

from famapy.metamodels.fm_metamodel.models.feature_model import FeatureModel, Feature, Relation, Constraint


class FeatureIDEParser(TextToModel):
    """Parser for FeatureIDE models (.xml)."""

    # Main tags
    TAG_STRUCT = 'struct'
    TAG_CONSTRAINTS = 'constraints'
    TAG_GRAPHICS = 'graphics'

    # Feature tags
    TAG_AND = 'and'
    TAG_OR = 'or'
    TAG_ALT = 'alt'

    # Constraints tags
    TAG_VAR = 'var'
    TAG_NOT = 'not'
    TAG_IMP = 'imp'
    TAG_DISJ = 'disj'
    TAG_CONJ = 'conj'
    TAG_EQ = 'eq'

    # Feature attributes
    ATTRIB_NAME = 'name'
    ATTRIB_ABSTRACT = 'abstract'
    ATTRIB_MANDATORY = 'mandatory'


    @staticmethod
    def get_source_extension() -> str:
        return 'xml'

    def __init__(self, path: str):
        self._path = path

    def transform(self) -> FeatureModel:
        return self._read_feature_model(self._path)

    def _read_feature_model(self, filepath: str) -> FeatureModel:
        tree = ET.parse(filepath)
        root = tree.getroot()
        for child in root:
            if child.tag == FeatureIDEParser.TAG_STRUCT:
                root = child[0]
                root_feature = Feature(name=root.attrib[FeatureIDEParser.ATTRIB_NAME], relations=[], parent=None)
                #root_feature.add_relation(Relation(parent=None, children=[], card_min=0, card_max=0))   # Relation for the parent.
                (features, children, relations) = self._read_features(root, root_feature)
                features = [root_feature] + features
                fm = FeatureModel(root_feature, [], features, relations)
            elif child.tag == FeatureIDEParser.TAG_CONSTRAINTS:
                if not self._no_read_constraints:
                    constraints = self._read_constraints(child, fm)
                    fm.ctcs.extend(constraints)
        return fm

    def _read_features(self, root_tree, parent: Feature) -> tuple[list[Feature], list[Relation]]:
        features = []
        children = []
        relations = []
        for child in root_tree:
            if not child.tag == FeatureIDEParser.TAG_GRAPHICS:
                #children = []
                is_abstract = False
                if FeatureIDEParser.ATTRIB_ABSTRACT in child.attrib and child.attrib[FeatureIDEParser.ATTRIB_ABSTRACT]:
                    is_abstract = True
                feature = Feature(name=child.attrib[FeatureIDEParser.ATTRIB_NAME], relations=[], parent=parent, is_abstract=is_abstract)
                #r = Relation(parent=parent, children=[], card_min=0, card_max=0)
                #feature.add_relation(r)   # Relation for the parent.
                features.append(feature)
                children.append(feature)
                #relations.append(r)
                if root_tree.tag == FeatureIDEParser.TAG_AND:
                    if FeatureIDEParser.ATTRIB_MANDATORY in child.attrib:  # Mandatory feature
                        r = Relation(parent=parent, children=[feature], card_min=1, card_max=1)
                        parent.add_relation(r)
                        relations.append(r)
                    else:  # Optional feature
                        r = Relation(parent=parent, children=[feature], card_min=0, card_max=1)
                        parent.add_relation(r)
                        relations.append(r)

                if child.tag == FeatureIDEParser.TAG_ALT:
                    (alt_children, direct_children, children_relations) = self._read_features(child, feature)
                    r = Relation(parent=feature, children=direct_children, card_min=1, card_max=1)
                    feature.add_relation(r)
                    features.extend(alt_children)
                    relations.append(r)
                    relations.extend(children_relations)
                elif child.tag == FeatureIDEParser.TAG_OR:
                    (or_children, direct_children, children_relations) = self._read_features(child, feature)
                    r = Relation(parent=feature, children=direct_children, card_min=1, card_max=len(direct_children))
                    feature.add_relation(r)
                    features.extend(or_children)
                    relations.append(r)
                    relations.extend(children_relations)
                elif child.tag == FeatureIDEParser.TAG_AND:
                    (and_children, direct_children, children_relations) = self._read_features(child, feature)
                    features.extend(and_children)
                    relations.extend(children_relations)
        return (features, children, relations)

    def _read_constraints(self, ctcs_root, fm: FeatureModel) -> list[Constraint]:
        n = 1
        constraints = []
        for ctc in ctcs_root:
            index = 0
            if ctc[index].tag == FeatureIDEParser.TAG_GRAPHICS:
                index += 1
            rule = ctc[index]
            str_ast = self._parse_rule(rule)
            if str_ast.startswith('('):
                str_ast = str_ast#[1:-1]
            if str_ast:
                ctc = Constraint(str(n), AST(str_ast))
                constraints.append(ctc)
            else:
                raise Exception()
            n += 1
        return constraints

    def _parse_rule(self, rule) -> str:
        """Return the representation of the constraint (rule) in the AST syntax."""
        str_ast = ''
        # print(f'Rule tag: {rule.tag}')
        # print(f'Rule values: {[r for r in rule]}')
        # print(f'Rule text: {rule.text}')
        if rule.tag == FeatureIDEParser.TAG_VAR:
            str_ast = rule.text
        elif rule.tag == FeatureIDEParser.TAG_NOT:
            str_ast = 'not ' + self._parse_rule(rule[0])
        elif rule.tag == FeatureIDEParser.TAG_IMP:
            str_ast = '(' + self._parse_rule(rule[0]) + ' implies ' + self._parse_rule(rule[1]) + ')'
        elif rule.tag == FeatureIDEParser.TAG_EQ:
            #str_ast = '(' + self._parse_rule(rule[0]) + ' eq ' + self._parse_rule(rule[1]) + ')'
            str_ast = '(' + self._parse_rule(rule[0]) + ' implies ' + self._parse_rule(rule[1]) + ') and (' + self._parse_rule(rule[1]) + ' implies ' + self._parse_rule(rule[0]) + ')'
        elif rule.tag == FeatureIDEParser.TAG_DISJ:
            str_ast = '(' + self._parse_rule(rule[0]) + ' or ' + self._parse_rule(rule[1]) + ')'
        elif rule.tag == FeatureIDEParser.TAG_CONJ:
            str_ast = '(' + self._parse_rule(rule[0]) + ' and ' + self._parse_rule(rule[1]) + ')'
            
        return str_ast