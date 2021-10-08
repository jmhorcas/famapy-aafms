from typing import Optional, Any
from enum import Enum


class ASTOperation(Enum):
    REQUIRES = 'REQUIRES'
    EXCLUDES = 'EXCLUDES'
    AND = 'AND'
    OR = 'OR'
    IMPLIES = 'IMPLIES'
    NOT = 'NOT'   
    EQUIVALENCE = 'EQUIVALENCE'


class Node:

    def __init__(self, data: Any):
        self.left: Optional['Node'] = None  # pylint: disable=unsubscriptable-object
        self.right: Optional['Node'] = None  # pylint: disable=unsubscriptable-object
        self.data = data

    def is_feature(self) -> bool:
        return not self.is_op()

    def is_op(self) -> bool:
        return isinstance(self.data, ASTOperation)

    def __str__(self) -> str:
        data = self.data.name if self.is_op() else self.data
            
        if self.left and self.right:
            return f'{data}[{self.left}][{self.right}]'

        if self.left and not self.right:
            return f'{data}[{self.left}][]'

        if not self.left and self.right:
            return f'{data}[][{self.right}]'

        return str(data)


class AST:
    """Abstract Syntax Tree (AST) to store constraints."""

    def __init__(self, root: Node):
        self.root = root

    @classmethod
    def create_simple_binary_operation(cls, operation: ASTOperation, left: str, right: str) -> 'AST':
        ast = cls(Node(operation))
        ast.root.left = Node(left)
        ast.root.right = Node(right)
        return ast

    @classmethod
    def create_simple_unary_operation(cls, operation: ASTOperation, elem: str) -> 'AST':
        ast = cls(Node(operation))
        ast.root.left = Node(elem)
        return ast
    
    @classmethod
    def create_binary_operation(cls, operation: ASTOperation, left: Node, right: Node) -> 'AST':
        ast = cls(Node(operation))
        ast.root.left = left
        ast.root.right = right
        return ast

    @classmethod
    def create_unary_operation(cls, operation: ASTOperation, elem: Node) -> 'AST':
        ast = cls(Node(operation))
        ast.root.left = elem
        return ast

    def to_cnf(self) -> 'AST':
        return convert_into_cnf(self)
        
    def __str__(self) -> str:
        return str(self.root)


def convert_into_cnf(ast: AST) -> AST:
    """Convert to negation normal form.

    Three steps are performed:
      1. Eliminate implications, equivalences, and excludes.
      2. Move NOTs inwards by repeatdly applying De Morgan's Law and eliminate doble negations.
      3. Distribute ORs invwards over ANDs, applying the Distribute property.
    """
    #print(f'Before: {ast}')
    completed = False
    while not completed:
        (ast, completed) = eliminate_complex_operators(ast)
    #print(f'eliminate_complex_operators: {ast}')
    completed = False
    while not completed:
        (ast, completed) = move_nots_inwards(ast)
    #print(f'move_nots_inwards: {ast}')
    completed = False
    while not completed:
        (ast, completed) = distribute_ors(ast)
    #print(f'distribute_ors: {ast}')
    return ast

def eliminate_implication(node: Node) -> Node:
    """Replace P => Q with !P ∨ Q."""
    left = AST.create_unary_operation(ASTOperation.NOT, node.left).root
    return AST.create_binary_operation(ASTOperation.OR, left, node.right).root

def eliminate_equivalence(node: Node) -> Node:
    """Replace P <=> Q with (P ∨ !Q) ∧ (!P ∨ Q)."""
    pnot = AST.create_unary_operation(ASTOperation.NOT, node.left).root
    qnot = AST.create_unary_operation(ASTOperation.NOT, node.right).root
    left = AST.create_binary_operation(ASTOperation.OR, node.left, qnot).root 
    right = AST.create_binary_operation(ASTOperation.OR, pnot, node.right).root 
    return AST.create_binary_operation(ASTOperation.AND, left, right).root 

def eliminate_exclusion(node: Node) -> Node:
    """Replace P EXCLUDES !Q with !P ∨ !Q."""
    left = AST.create_unary_operation(ASTOperation.NOT, node.left).root
    right = AST.create_unary_operation(ASTOperation.NOT, node.right).root
    return AST.create_binary_operation(ASTOperation.OR, left, right).root 

def eliminate_complex_operators(ast: AST) -> tuple[AST,bool]:
    """Eliminate imlications, equivalences, and excludes"""
    node = ast.root
    stack = []
    stack.append(node)
    new_root = None
    found_any = False
    while stack:
        n = stack.pop()
        #print(f'Node: {n} - {n.is_op()}, {n.data}')
        if n is not None and n.is_op():
            new_node = None
            if n.data == ASTOperation.REQUIRES or n.data == ASTOperation.IMPLIES:
                new_node = eliminate_implication(n)
                found_any = True
            elif n.data == ASTOperation.EQUIVALENCE:
                new_node = eliminate_implication(n)
                found_any = True
            elif n.data == ASTOperation.EXCLUDES:
                new_node = eliminate_exclusion(n)
                found_any = True
            elif n.data == ASTOperation.NOT:
                stack.append(n.left)
            else:  # OR, AND nodes
                stack.append(n.left)
                stack.append(n.right)

            if new_node is not None:
                stack.append(new_node.left)
                stack.append(new_node.right)
            
            if new_root is None:
                if new_node is not None:
                    new_root = new_node
                else:
                    new_root = n
    return (AST(new_root), not found_any)

def apply_demorganlaw(node: Node, operation: ASTOperation) -> Node:
    """Apply De Morgan's Law.
        
    If operation is AND, replace !(P ∨ Q) with (!P) ∧ (!Q);
    if operation is OR, replace !(P ∧ Q) with (!P) ∨ (!Q).
    """
    left = AST.create_unary_operation(ASTOperation.NOT, node.left).root
    right = AST.create_unary_operation(ASTOperation.NOT, node.right).root
    new_node = AST.create_binary_operation(operation, left, right).root
    return new_node

def move_nots_inwards(ast: AST) -> tuple[AST,bool]:
    """Move NOTs inwards by repeatedly applying De Morgan's Law, 
    and eliminate doble negations by replacing !!P with P.
    """
    node = ast.root
    stack = []
    stack.append(node)
    new_root = None
    found_any = False
    while stack:
        n = stack.pop()
        if n is not None and n.is_op():
            new_node = None
            if n.data == ASTOperation.NOT:
                if n.left.is_op():
                    if n.left.data == ASTOperation.OR:
                        new_node = apply_demorganlaw(ASTOperation.AND, n)
                        found_any = True
                    elif n.left.data == ASTOperation.AND:
                        new_node = apply_demorganlaw(ASTOperation.OR, n)
                        found_any = True
                    elif n.left.data == ASTOperation.NOT:
                        # Eliminate doble negation
                        new_node = n.left.left
                        found_any = True
                    else:  # OR, AND nodes
                        stack.append(n.left)
                        stack.append(n.right)

            if new_node is not None:
                stack.append(new_node.left)
                stack.append(new_node.right)
            
            if new_root is None:
                if new_node is not None:
                    new_root = new_node
                else:
                    new_root = n
    return (AST(new_root), not found_any)

def apply_distribution(node: Node, and_node: Node) -> Node:
    """Apply distribution property.
    
    Replace P ∨ (Q ∧ R) with (P ∨ Q) ∧ (P ∨ R).
    """
    left = AST.create_binary_operation(ASTOperation.OR, node.left, and_node.left).root
    right = AST.create_binary_operation(ASTOperation.OR, node.left, and_node.right).root
    return AST.create_binary_operation(ASTOperation.AND, left, right).root


def distribute_ors(ast: AST) -> tuple[AST,bool]:
    """Distribute ORs inwards over ANDs."""
    node = ast.root
    stack = []
    stack.append(node)
    new_root = None
    found_any = False
    while stack:
        n = stack.pop()
        if n is not None and n.is_op():
            new_node = None
            if n.data == ASTOperation.OR:
                if n.left.is_op():
                    if n.left.data == ASTOperation.AND:
                        new_node = apply_distribution(n, n.left)
                        found_any = True
                    elif n.left.data == ASTOperation.NOT and n.left.left.data == ASTOperation.AND:
                        # Cuidado aquí, falta hacer la distributiva cuando hay negaciones.
                    elif n.right.data == ASTOperation.AND:
                        new_node = apply_distribution(n, n.right) 
                        found_any = True
                    else:
                        stack.append(n.left)
                        stack.append(n.right)

                    if new_node is not None:
                        stack.append(new_node.left)
                        stack.append(new_node.right)
            
            if new_root is None:
                if new_node is not None:
                    new_root = new_node
                else:
                    new_root = n
    return (AST(new_root), not found_any)
