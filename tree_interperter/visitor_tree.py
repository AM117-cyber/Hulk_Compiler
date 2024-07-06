from cmp import visitor
from grammar.ast_nodes import *

class VisitorTree:
    def __init__(self) -> None:
        pass

    @visitor.on('node')
    def visit(self, node, scope):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode):
        