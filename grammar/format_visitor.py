from cmp.visitor import on, when
from grammar.ast_nodes import *

class FormatVisitor:
    @on('node')
    def visit(self, node, tabs=0):
        pass

    @when(ProgramNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__ProgramNode [<decl>, ...,<decl>] <expr>'
        declarations = '\n'.join(self.visit(decl, tabs + 1) for decl in node.declarations)
        expression = self.visit(node.expression, tabs + 1)
        return f'{ans}\n{declarations}\n{expression}'

    @when(MethodSignatureNode)
    def visit(self, node, tabs=0):
        # params = ', '.join(':'.join(param) for param in node.params)
        params = ', '.join(':'.join((param[0], str(param[1]) if param[1] is None else param[1])) for param in node.params)
        ans = '\t' * tabs + f'\\__MethodSignatureNode: {node.name}({params}) : {node.returnType}'
        return ans

    @when(FunctionDeclarationNode)
    def visit(self, node, tabs=0):
        params = ', '.join(':'.join((param[0], str(param[1]) if param[1] is None else param[1])) for param in node.params)
        ans = '\t' * tabs + f'\\__FunctionDeclarationNode: {node.name}({params}): {node.returnType} -> <expr>'
        body = self.visit(node.body, tabs + 1)
        return f'{ans}\n{body}'
    
    @when(MethodDeclarationNode)
    def visit(self, node, tabs=0):
        params = ', '.join(':'.join((param[0], str(param[1]) if param[1] is None else param[1])) for param in node.params)
        ans = '\t' * tabs + f'\\__MethodDeclarationNode: {node.name}({params}): {node.returnType} -> <expr>'
        body = self.visit(node.body, tabs + 1)
        return f'{ans}\n{body}'

    # @when(TypeConstructorSignatureNode)
    # def visit(self, node, tabs=0):
    #     params = ', '.join(node.params)
    #     ans = '\t' * tabs + f'\\__TypeConstructorSignatureNode: {node.name}({params})'
    #     return ans

    @when(TypeAttributeNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__TypeAttributeNode: {node.name} : {node.type} = <expr>'
        expression = self.visit(node.value, tabs + 1)
        return f'{ans}\n{expression}'

    @when(TypeDeclarationNode)
    def visit(self, node, tabs=0):
        # params = ', '.join(node.params)
        params = ', '.join(':'.join((param[0], str(param[1]) if param[1] is None else param[1])) for param in node.params)
        ans = '\t' * tabs + f'\\__TypeDeclarationNode: {node.name}({params}) inherits {node.parent} (<expr>,...,<expr>) -> <body>'
        parent_args = '\n'.join(self.visit(f_arg, tabs + 1) for f_arg in node.parent_args)
        attributes = '\n'.join(self.visit(attr, tabs + 1) for attr in node.attributes)
        methods = '\n'.join(self.visit(method, tabs + 1) for method in node.methods)
        return f'{ans}\n{parent_args}\n{attributes}\n{methods}'

    @when(ProtocolDeclarationNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__ProtocolDeclarationNode: {node.name} extends {node.parent} -> body'
        methods = '\n'.join(self.visit(method, tabs + 1) for method in node.methods)
        return f'{ans}\n{methods}'

    @when(VarDeclarationNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__VarDeclarationNode: {node.name} : {node.type} = <expr>'
        expression = self.visit(node.value, tabs + 1)
        return f'{ans}\n{expression}'

    @when(ConditionalNode)
    def visit(self, node, tabs=0):
        # ans = '\t' * tabs + f'\\__ConditionalNode: if (<expr>) <expr> elif (<expr>) <expr> else <expr>'
        ans = '\t' * tabs + f'\\__ConditionalNode: [<expr>,...,<expr>] [<expr>,...,<expr>] <expr>'
        # conditions = '\n'.join(self.visit(cond, tabs + 1) for cond in node.conditions)
        # expressions = '\n'.join(self.visit(expr, tabs + 1) for expr in node.expressions)

        conditions_expressions = '\n'.join(
        '\t' * (tabs+1)+'Condition:\n'+f'{self.visit(cond, tabs + 1)}' + '\n'+
        '\t' * (tabs+1)+'Then:\n' +f'{self.visit(expr, tabs + 1)}'
        for cond, expr in zip(node.conditions, node.expressions)
        )

        default = '\t' * (tabs+1)+'Default: \n'+self.visit(node.default, tabs + 1)
        return f'{ans}\n{conditions_expressions}\n{default}'

    @when(LetInNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__LetInNode: let [<var_decl>...<var_decl>] in <expr>'
        variables = '\n'.join(self.visit(var, tabs + 1) for var in node.variables)
        body = self.visit(node.body, tabs + 1)
        return f'{ans}\n{variables}\n{body}'

    @when(WhileNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__WhileNode: while <expr> -> <expr>'
        condition = self.visit(node.condition, tabs + 1)
        body = self.visit(node.body, tabs + 1)
        return f'{ans}\n{condition}\n{body}'

    @when(ForNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__ForNode: for {node.item} in <expr> -> <expr>'
        iterable = self.visit(node.iterable, tabs + 1)
        body = self.visit(node.body, tabs + 1)
        return f'{ans}\n{iterable}\n{body}'

    @when(DestrNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__DestrNode: {node.var} := <expr>'
        expr = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{expr}'

    @when(BinaryNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__<expr> {node.__class__.__name__} <expr>'
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        return f'{ans}\n{left}\n{right}'

    @when(UnaryNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__{node.__class__.__name__} <expr>'
        operand = self.visit(node.operand, tabs + 1)
        return f'{ans}\n{operand}'

    @when(LiteralNode)
    def visit(self, node, tabs=0):
        return '\t' * tabs + f'\\__{node.__class__.__name__} : {node.lex}'

    @when(ExpressionBlockNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__ExpressionBlockNode {{<expr>;...;<expr>;}}'
        expressions = '\n'.join(self.visit(expr, tabs + 1) for expr in node.expressions)
        return f'{ans}\n{expressions}'

    @when(CallFuncNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__CallFuncNode: {node.name}(<expr>, ..., <expr>)'
        arguments = '\n'.join(self.visit(arg, tabs + 1) for arg in node.arguments)
        return f'{ans}\n{arguments}'

    @when(TypeInstantiationNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__TypeInstantiationNode: {node.name}(<expr>, ..., <expr>)'
        arguments = '\n'.join(self.visit(arg, tabs + 1) for arg in node.arguments)
        return f'{ans}\n{arguments}'

    @when(ExplicitVectorNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__ExplicitVectorNode: [<expr>,...,<expr>]'
        items = '\n'.join(self.visit(item, tabs + 1) for item in node.items)
        return f'{ans}\n{items}'

    @when(ImplicitVectorNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__ImplicitVectorNode: [<expr> || {node.item} in <expr>]'
        expr = self.visit(node.expr, tabs + 1)
        iterable = self.visit(node.iterable, tabs + 1)
        return f'{ans}\n{expr}\n{iterable}'

    @when(IndexObjectNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__IndexObjectNode: <atom> [<expr>]'
        obj = self.visit(node.object, tabs + 1)
        pos = self.visit(node.pos, tabs + 1)
        return f'{ans}\n{obj}\n{pos}'

    @when(CallMethodNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__CallMethodNode: <atom>.{node.method_name}(<expr>, ..., <expr>)'
        inst_name = self.visit(node.inst_name, tabs + 1)
        args = '\n'.join(self.visit(arg, tabs + 1) for arg in node.method_args)
        return f'{ans}\n{inst_name}\n{args}'

    @when(CallTypeAttributeNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__CallTypeAttributeNode: <atom>.{node.attribute}'
        inst_name = self.visit(node.inst_name, tabs + 1)
        return f'{ans}\n{inst_name}'

    @when(CastTypeNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__CastTypeNode: <atom> as {node.type_cast}'
        inst_name = self.visit(node.inst_name, tabs + 1)
        return f'{ans}\n{inst_name}'
    
    @when(CheckTypeNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__<expr> CheckTypeNode <expr>'
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        return f'{ans}\n{left}\n{right}'
    
