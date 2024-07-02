from lexer.automata import NFA
from lexer.automata_tools import automata_closure, automata_concatenation, automata_union
EPSILON = 'ε'

class Node:
    def evaluate(self):
        raise NotImplementedError()
        
class AtomicNode(Node):
    def __init__(self, lex):
        self.lex = lex

class UnaryNode(Node):
    def __init__(self, node):
        self.node = node
        
    def evaluate(self):
        value = self.node.evaluate() 
        return self.operate(value)
    
    @staticmethod
    def operate(value):
        raise NotImplementedError()
        
class BinaryNode(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        
    def evaluate(self):
        lvalue = self.left.evaluate() 
        rvalue = self.right.evaluate()
        return self.operate(lvalue, rvalue)
    
    @staticmethod
    def operate(lvalue, rvalue):
        raise NotImplementedError()
    
from cmp.ast import get_printer
printer = get_printer(AtomicNode=AtomicNode, UnaryNode=UnaryNode, BinaryNode=BinaryNode)

class EpsilonNode(AtomicNode):
    def evaluate(self):
        # Your code here!!!
        return NFA(states=1, finals=[0], transitions={})
    
class SymbolNode(AtomicNode):
    def evaluate(self):
        s = self.lex
        # Your code here!!!
        return NFA(states = 2, finals=[1], transitions={
            (0, s): [1]
        })
    
class ClosureNode(UnaryNode):
    @staticmethod
    def operate(value):
        # Your code here!!!
        return automata_closure(value)
    
class UnionNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        # Your code here!!!
        return automata_union(lvalue, rvalue)
    
class ConcatNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        # Your code here!!!
        return automata_concatenation(lvalue, rvalue)    
