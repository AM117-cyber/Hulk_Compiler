from typing import List, Tuple
from cmp.semantic import Context


class Node:
    pass
    def evaluate(self, context:Context):
        raise NotImplementedError()

#--------------------------------------------Depth 1---------------------------------------------

class ProgramNode(Node):
    def __init__(self, declarations, expression):
        self.declarations = declarations
        self.expression = expression
    def evaluate(self, context:Context):
        return self.expression.evaluate()
        
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
    def evaluate(self, context: Context):
        self.scope.find_variable(self.name).set_value(self.value.evaluate())

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
        self.conditions, self.expressions = zip(*conditions_expr)

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

class UnaryNode(ExpressionNode):
    def __init__(self, operand):
        self.operand = operand

#-----------------------------------------------Depth 3----------------------------------------------------------------
#_________________________________________________________________________________________________________________________
#________________________________________________Binary__________________________________________________________________
class BooleanBinaryNode(BinaryNode):
    pass

class ComparisonBinaryNode(BinaryNode):
    pass

class StringBinaryNode(BinaryNode):
    pass

class ArithmeticBinaryNode(BinaryNode):
    pass

class CheckTypeNode(BinaryNode):
    pass
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
    pass

class AndNode(BooleanBinaryNode):
    pass

class NotNode(BooleanUnaryNode):
    pass
#_________________________________________________________________________________________________________________________
#________________________________________________Comparisons__________________________________________________________________
class EqualNode(ComparisonBinaryNode):
    pass

class NotEqualNode(ComparisonBinaryNode):
    pass

class GreaterNode(ComparisonBinaryNode):
    pass

class GreaterEqualNode(ComparisonBinaryNode):
    pass

class LessNode(ComparisonBinaryNode):
    pass

class LessEqualNode(ComparisonBinaryNode):
    pass
#_________________________________________________________________________________________________________________________
#___________________________________________________Strings__________________________________________________________________
class ConcatNode(StringBinaryNode):
    pass

class DoubleConcatNode(StringBinaryNode):
    pass
#_________________________________________________________________________________________________________________________
#__________________________________________________Arithmetic__________________________________________________________________

class PlusNode(ArithmeticBinaryNode):
    pass

class MinusNode(ArithmeticBinaryNode):
    pass

class MultNode(ArithmeticBinaryNode):
    pass

class DivNode(ArithmeticBinaryNode):
    pass

class ModNode(ArithmeticBinaryNode):
    pass

class PowNode(ArithmeticBinaryNode):
    pass

class PositiveNode(ArithmeticUnaryNode):
    pass

class NegativeNode(ArithmeticUnaryNode):
    pass


#_________________________________________________________________________________________________________________________
#__________________________________________________Literals__________________________________________________________________
class BooleanNode(LiteralNode):
    pass

class VarNode(LiteralNode):
    pass

class NumberNode(LiteralNode):
    pass

class StringNode(LiteralNode):
    pass