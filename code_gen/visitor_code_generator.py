from cmp import visitor
from grammar.ast_nodes import *


class VisitorCodeGenerator:
    def __init__(self, context):
        self.id_conditional_expr = 0
        self.conditional_expr = ''
    
    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ConditionalNode) 
    def visit(self, node : ConditionalNode):
        var_locals = node.scope.get_variables()
        cond_params = '('

        for var in var_locals:
            cond_params += var.nameC 

        length = 0

        conditions = '['
        for cond in node.conditions:
            conditions += self.visit(cond) + ', '
            length += 1
        conditions = conditions[:-2]
        conditions += ']'

        expressions = '['
        for expr in node.expressions:
            expressions += self.visit(expr) + ', '
        expressions = expressions[:-2]
        expressions += ']'

        default = self.visit(node.default)

        return '\tconditionalExpr' + self.id_conditional_expr
    
    @visitor.when(LetInNode) # Incompleto
    def visit(self, node : LetInNode):
        length = 0
        variables = '['
        for var in node.variables:
            variables += self.visit(var) + ', '
            length += 1
        variables = variables[:-2]
        variables += ']'

        return ''



    
