from typing import List, Tuple
from cmp.semantic import *
from cmp.semantic import Context


class Node:
    row = 0
    column = 0
    scope = None

#--------------------------------------------Depth 1---------------------------------------------

class ProgramNode(Node):
    def __init__(self, declarations, expression):
        self.declarations = declarations
        self.expression = expression
        
class DeclarationNode(Node):
    pass
        
class ExpressionNode(Node):
    pass

#--------------------------------------------Depth 2---------------------------------------------
#_____________________________________________________________________________________________________
#__________________________________________Declarations__________________________________________________________________
class MethodSignatureNode(DeclarationNode):
    def __init__(self, name, params, returnType = None):
        self.name = name
        self.params = params
        self.returnType = returnType

class MethodDeclarationNode(DeclarationNode):
    def __init__(self, signature: MethodSignatureNode, body):
        self.name = signature.name
        self.params = signature.params
        self.returnType = signature.returnType
        self.body = body

class FunctionDeclarationNode(DeclarationNode):
    def __init__(self, method: MethodDeclarationNode):
        self.name = method.name
        self.params = method.params
        self.returnType = method.returnType
        self.body = method.body

class TypeConstructorSignatureNode(DeclarationNode):
    def __init__(self, name, params = []):
        self.name = name
        self.params = params

class TypeAttributeNode(DeclarationNode):
    def __init__(self, name, value, type = None):
        self.name = name
        self.value = value
        self.type = type

class TypeDeclarationNode(DeclarationNode):
    def __init__(self, signature: TypeConstructorSignatureNode, body, parent = 'Object', father_args = []):
        self.name = signature.name
        self.params = signature.params
        self.parent = parent
        self.parent_args = father_args
        self.attributes = [attribute for attribute in body if isinstance(attribute, TypeAttributeNode)]
        self.methods = [method for method in body if isinstance(method, MethodDeclarationNode)]


class ProtocolDeclarationNode(DeclarationNode):
    def __init__(self, name, methods_signature: List[MethodSignatureNode], parent = None):
        self.name = name
        self.methods = methods_signature
        self.parent = parent

class VarDeclarationNode(DeclarationNode):
    def __init__(self, name, value, type = None):
        self.name = name
        self.value = value
        self.type = type
#_________________________________________________________________________________________________________________________
#__________________________________________Expressions__________________________________________________________________

class ConditionalNode(ExpressionNode):
    def __init__(self,conditions_expr: List[Tuple]):
        self.default = (conditions_expr.pop())[1]
        conditions,expressions = zip(*conditions_expr)
        self.conditions = list(conditions)
        self.expressions = list(expressions)

class LetInNode(ExpressionNode):
    def __init__(self, variables: List[VarDeclarationNode], body):
        self.variables = variables
        self.body = body
    

class WhileNode(ExpressionNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class ForNode(ExpressionNode):
    def __init__(self, item, iterable, body):
        self.item = item
        self.iterable = iterable
        self.body = body

class DestrNode(ExpressionNode):
    def __init__(self, var , expr):
        self.var = var
        self.expr = expr

class AtomicNode(ExpressionNode):
    pass

class BinaryNode(ExpressionNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.operator = None

class UnaryNode(ExpressionNode):
    def __init__(self, operand):
        self.operand = operand
        self.operator = None

#-----------------------------------------------Depth 3----------------------------------------------------------------
#_________________________________________________________________________________________________________________________
#________________________________________________Binary__________________________________________________________________
class BooleanBinaryNode(BinaryNode):
    pass

class ComparisonBinaryNode(BinaryNode):
    pass

class EqualityBinaryNode(BinaryNode):
    pass

class StringBinaryNode(BinaryNode):
    pass

class ArithmeticBinaryNode(BinaryNode):
    pass

class CheckTypeNode(ExpressionNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        
#_________________________________________________________________________________________________________________________
#_________________________________________________Unary__________________________________________________________________

class ArithmeticUnaryNode(UnaryNode):
    pass

class BooleanUnaryNode(UnaryNode):
    pass

#_________________________________________________________________________________________________________________________
#_________________________________________________Atoms__________________________________________________________________

class LiteralNode(AtomicNode):
    def __init__(self, lex):
        self.lex = lex

class ExpressionBlockNode(AtomicNode):
    def __init__(self, expressions):
        self.expressions = expressions
        

class CallFuncNode(AtomicNode):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class TypeInstantiationNode(AtomicNode):
    def __init__(self, type_inst:CallFuncNode):
        self.name = type_inst.name
        self.arguments = type_inst.arguments


class ExplicitVectorNode(AtomicNode):
    def __init__(self, items):
        self.items = items

class ImplicitVectorNode(AtomicNode):
    def __init__(self, expr, item, iterable):
        self.expr = expr
        self.item = item
        self.iterable = iterable


class IndexObjectNode(AtomicNode):
    def __init__(self, object, pos):
        self.object = object
        self.pos = pos
    

class CallMethodNode(AtomicNode):
    def __init__(self, inst_name, method: CallFuncNode):
        self.inst_name = inst_name
        self.method_name = method.name
        self.method_args = method.arguments
    
class CallTypeAttributeNode(AtomicNode):
    def __init__(self, inst_name , attribute):
        self.inst_name = inst_name
        self.attribute = attribute

class CastTypeNode(AtomicNode):
    def __init__(self, inst_name , type_cast):
        self.inst_name = inst_name
        self.type_cast = type_cast

#---------------------------------------------------Depth 4---------------------------------------------------------------------
#_________________________________________________________________________________________________________________________
#___________________________________________________Boolean__________________________________________________________________
class OrNode(BooleanBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '|'

class AndNode(BooleanBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '&'

class NotNode(BooleanUnaryNode):
    def __init__(self, operand):
        super().__init__(operand)
        self.operator = '!'
#_________________________________________________________________________________________________________________________
#________________________________________________Comparisons__________________________________________________________________
class EqualNode(EqualityBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '=='

class NotEqualNode(EqualityBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '!='

class GreaterNode(ComparisonBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '>'

class GreaterEqualNode(ComparisonBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '>='

class LessNode(ComparisonBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '<'

class LessEqualNode(ComparisonBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '<='
#_________________________________________________________________________________________________________________________
#___________________________________________________Strings__________________________________________________________________
class ConcatNode(StringBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '@'

class DoubleConcatNode(StringBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '@@'
#_________________________________________________________________________________________________________________________
#__________________________________________________Arithmetic__________________________________________________________________

class PlusNode(ArithmeticBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '+'

class MinusNode(ArithmeticBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '-'

class MultNode(ArithmeticBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '*'

class DivNode(ArithmeticBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '/'

class ModNode(ArithmeticBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '%'

class PowNode(ArithmeticBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '**'

class PositiveNode(ArithmeticUnaryNode):
    def __init__(self, operand):
        super().__init__(operand)
        self.operator = '+'

class NegativeNode(ArithmeticUnaryNode):
    def __init__(self, operand):
        super().__init__(operand)
        self.operator = '-'


#_________________________________________________________________________________________________________________________
#__________________________________________________Literals__________________________________________________________________
class BooleanNode(LiteralNode):
    def __init__(self, lex):
        super().__init__(lex)

class VarNode(LiteralNode):
    def __init__(self, lex):
        super().__init__(lex)

class NumberNode(LiteralNode):
    def __init__(self, lex):
        super().__init__(lex)

class StringNode(LiteralNode):
    def __init__(self, lex):
        super().__init__(lex)