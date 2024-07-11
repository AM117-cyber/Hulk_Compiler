from typing import List, Tuple
from cmp.semantic import *
from cmp.semantic import Context


class Node:
    def __init__(self) -> None:
        self.scope:Scope = None

    def evaluate(self, context: Context):
        raise NotImplementedError()

#--------------------------------------------Depth 1---------------------------------------------

class ProgramNode(Node):
    def __init__(self, declarations, expression):
        self.declarations = declarations
        self.expression = expression
    def evaluate(self, context: Context):
        for decl in self.declarations:
            decl.evaluate(context)
        
        return self.expression.evaluate(context)
        
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
        value, _ = self.value.evaluate(context)
        self.scope.find_variable(self.name).set_value(value)

class TypeDeclarationNode(DeclarationNode):
    def __init__(self, signature: TypeConstructorSignatureNode, body, parent = 'Object', father_args = []):
        self.name = signature.name
        self.params = signature.params
        self.parent = parent
        self.parent_args = father_args
        self.attributes = [attribute for attribute in body if isinstance(attribute, TypeAttributeNode)]
        self.methods = [method for method in body if isinstance(method, MethodDeclarationNode)]
    def evaluate(self, context: Context):
        pass


class ProtocolDeclarationNode(DeclarationNode):
    def __init__(self, name, methods_signature: List[MethodSignatureNode], parent = None):
        self.name = name
        self.methods = methods_signature
        self.parent = parent
    def evaluate(self, context: Context):
        pass

class VarDeclarationNode(DeclarationNode):
    def __init__(self, name, value, type = None):
        self.name = name
        self.value = value
        self.type = type
    def evaluate(self, context: Context):
        value, _ = self.value.evaluate(context)
        self.scope.find_variable(self.name).set_value(value)
#_________________________________________________________________________________________________________________________
#__________________________________________Expressions__________________________________________________________________

class ConditionalNode(ExpressionNode):
    def __init__(self,conditions_expr: List[Tuple]):
        self.default = (conditions_expr.pop())[1]
        conditions,expressions = zip(*conditions_expr)
        self.conditions = list(conditions)
        self.expressions = list(expressions)
    def evaluate(self, context: Context):
        for cond, expr in zip(self.conditions, self.expressions):
            cond_value, _ = cond.evaluate(context)
            if cond_value:
                return expr.evaluate(context)
        
        return self.default.evaluate(context)


class LetInNode(ExpressionNode):
    def __init__(self, variables: List[VarDeclarationNode], body):
        self.variables = variables
        self.body = body
    def evaluate(self, context: Context):
        for var in self.variables:
            var.evaluate(context)

        return self.body.evaluate(context) 
    

class WhileNode(ExpressionNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    def evaluate(self, context: Context):
        body_value = None
        body_type = None
        cond_value, _ = self.condition.evaluate(context)
        while cond_value:
            body_value, body_type = self.body.evaluate(context)
            cond_value, _ = self.condition.evaluate(context)

        return body_value, body_type

class ForNode(ExpressionNode):
    def __init__(self, item, iterable, body):
        self.item = item
        self.iterable = iterable
        self.body = body
    def evaluate(self, context: Context):
        body_value = None
        body_type = None
        for item in self.iterable:
            item_value, _ = item.evaluate(context)
            self.item.scope.find_variable(self.item.lex).set_value(item_value)
            body_value, body_type = self.body.evaluate(context)

        return body_value, body_type

class DestrNode(ExpressionNode):
    def __init__(self, var , expr):
        self.var = var
        self.expr = expr
    def evaluate(self, context: Context):
        value, _ = self.expr.evaluate(context)
        self.scope.find_variable(self.var.lex).set_value(value)

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

class EqualityBinaryNode(BinaryNode):
    pass

class StringBinaryNode(BinaryNode):
    pass

class ArithmeticBinaryNode(BinaryNode):
    pass

class CheckTypeNode(BinaryNode):
    def evaluate(self, context: Context):
        _, left_type = self.left.evaluate(context)
        _, right_type = self.right.evaluate(context)
        is_left_protocol = isinstance(left_type, Protocol)
        is_right_protocol = isinstance(right_type, Protocol)

        if is_left_protocol and not is_right_protocol:
            raise SemanticError(f'A protocol can\'t conforms to a type')
        
        return left_type.conforms_to(right_type), BooleanType()  
        
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
    def evaluate(self, context: Context):
        expr_value = None
        expr_type = None
        for expr in self.expressions:
            expr_value, expr_type = expr.evaluate(context)

        return expr_value, expr_type
        

class CallFuncNode(AtomicNode):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

    def evaluate(self, context: Context):
        arguments = []
        for argum in self.arguments:
            argum_value, argum_type = argum.evaluate(context)
            arguments.append((argum_value, argum_type))

        try:    
            value_builtin_func, bool_value, type_builtin_func = context.execute_builtin_functions(self.name, arguments)
        except SemanticError as error:
            raise SemanticError(error)
        else:
            if bool_value:
                return value_builtin_func, type_builtin_func
            else:
                func = context.functions[self.name]
                for param, argum in zip(func.node.params, arguments):
                    func.node.scope.find_variable(param).set_value(argum[0])
                
                return func.node.evaluate(context)

class TypeInstantiationNode(AtomicNode):
    def __init__(self, type_inst:CallFuncNode):
        self.name = type_inst.name
        self.arguments = type_inst.arguments
    def evaluate(self, context: Context):
        type_ = context.types[self.name]
        for param, argum in zip(type_.node.param_names, self.arguments):
            type_.node.scope.find_variable(param).set_value(argum)
        
        type_.node.evaluate(context)
        return type_.node, type_


class ExplicitVectorNode(AtomicNode):
    def __init__(self, items):
        self.items = items
    def evaluate(self, context: Context):
        items_values = []
        items_type = None
        for item in self.items:
            value, items_type = item.evaluate(context)
            items_values.append(value)

        return items_values, items_type

class ImplicitVectorNode(AtomicNode):
    def __init__(self, expr, item, iterable):
        self.expr = expr
        self.item = item
        self.iterable = iterable
    def evaluate(self, context: Context):
        expr_values = []
        expr_type = None
        for item in self.iterable:
            item_value, _ = item.evaluate(context)
            self.item.scope.find_variable(self.item.lex).set_value(item_value)
            expr_value, expr_type = self.expr.evaluate(context)
            expr_values.append(expr_value)

        return expr_values, expr_type


class IndexObjectNode(AtomicNode):
    def __init__(self, object, pos):
        self.object = object
        self.pos = pos
    def evaluate(self, context: Context):
        index = 0
        size_object = len(self.object)
        if self.pos < 0 or self.pos > size_object-1:
            raise SemanticError('Index out of range')

        for obj in self.object:
            if index == self.pos:
                return obj.evaluate(context)
            index += 1
    

class CallMethodNode(AtomicNode):
    def __init__(self, inst_name, method: CallFuncNode):
        self.inst_name = inst_name
        self.method_name = method.name
        self.method_args = method.arguments
    def evaluate(self, context: Context):
        var = self.scope.find_variable(self.inst_name)

        for param, argum in zip(var.type.methods[self.method_name].param_names, self.method_args):
            var.type.methods[self.method_name].node.scope.find_variable(param).set_value(argum)

        return var.type.methods[self.method_name].node.evaluate(context)

class CallTypeAttributeNode(AtomicNode):
    def __init__(self, inst_name , attribute):
        self.inst_name = inst_name
        self.attribute = attribute
    def evaluate(self, context: Context):
        return self.attribute.evaluate(context)

class CastTypeNode(AtomicNode):
    def __init__(self, inst_name , type_cast):
        self.inst_name = inst_name
        self.type_cast = type_cast
    def evaluate(self, context: Context):
        _, inst_type = self.inst_name.evaluate(context)
        type_cast = context.types[self.type_cast.lex]
        is_inst_protocol = isinstance(inst_type, Protocol)
        is_type_cast_protocol = isinstance(type_cast, Protocol)

        if is_type_cast_protocol and not is_inst_protocol:
            raise SemanticError(f'A protocol can\'t conforms to a type')
        
        return type_cast.conforms_to(inst_type), BooleanType()

#---------------------------------------------------Depth 4---------------------------------------------------------------------
#_________________________________________________________________________________________________________________________
#___________________________________________________Boolean__________________________________________________________________
class OrNode(BooleanBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
    def evaluate(self, context: Context):
        left_value, _ = self.left.evaluate(context)
        right_value, _ = self.right.evaluate(context)
        or_value = False

        try:
            or_value = left_value | right_value
        except:
            raise SemanticError(f'Or-Operation is not defined between "{left_value}" and "{right_value}"')
        
        return or_value, BooleanType()

class AndNode(BooleanBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
    def evaluate(self, context: Context):
        left_value, _ = self.left.evaluate(context)
        right_value, _ = self.right.evaluate(context)
        and_value = False

        try:
            and_value = left_value & right_value
        except:
            raise SemanticError(f'And-Operation is not defined between "{left_value}" and "{right_value}"')
        
        return and_value, BooleanType()

class NotNode(BooleanUnaryNode):
    def __init__(self, operand):
        super().__init__(operand)
    def evaluate(self, context: Context):
        operand_value, _ = self.operand.evaluate(context)
        not_value = False

        try:
            not_value = not operand_value
        except:
            raise SemanticError(f'Not-Operation is not defined for "{operand_value}"')
        
        return not_value, BooleanType()
#_________________________________________________________________________________________________________________________
#________________________________________________Comparisons__________________________________________________________________
class EqualNode(EqualityBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
    def evaluate(self, context: Context):
        left_value, _ = self.left.evaluate(context)
        right_value, _ = self.right.evaluate(context)
        equal_value = False

        try:
            equal_value = left_value == right_value
        except:
            raise SemanticError(f'Equal-Operation is not defined between "{left_value}" and "{right_value}"')
        
        return equal_value, BooleanType()

class NotEqualNode(EqualityBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
    def evaluate(self, context: Context):
        left_value, _ = self.left.evaluate(context)
        right_value, _ = self.right.evaluate(context)
        not_equal_value = False

        try:
            not_equal_value = left_value != right_value
        except:
            raise SemanticError(f'Not_Equal-Operation is not defined between "{left_value}" and "{right_value}"')
        
        return not_equal_value, BooleanType()

class GreaterNode(ComparisonBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
    def evaluate(self, context: Context):
        left_value, _ = self.left.evaluate(context)
        right_value, _ = self.right.evaluate(context)
        greater_value = False

        try:
            greater_value = left_value > right_value
        except:
            raise SemanticError(f'Greater-Operation is not defined between "{left_value}" and "{right_value}"')
        
        return greater_value, BooleanType()

class GreaterEqualNode(ComparisonBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
    def evaluate(self, context: Context):
        left_value, _ = self.left.evaluate(context)
        right_value, _ = self.right.evaluate(context)
        greater_equal_value = False

        try:
            greater_equal_value = left_value >= right_value
        except:
            raise SemanticError(f'GreaterEqual-Operation is not defined between "{left_value}" and "{right_value}"')
        
        return greater_equal_value, BooleanType()

class LessNode(ComparisonBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
    def evaluate(self, context: Context):
        left_value, _ = self.left.evaluate(context)
        right_value, _ = self.right.evaluate(context)
        less_value = False

        try:
            less_value = left_value < right_value
        except:
            raise SemanticError(f'Less-Operation is not defined between "{left_value}" and "{right_value}"')
        
        return less_value, BooleanType()

class LessEqualNode(ComparisonBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
    def evaluate(self, context: Context):
        left_value, _ = self.left.evaluate(context)
        right_value, _ = self.right.evaluate(context)
        less_equal_value = False

        try:
            less_equal_value = left_value <= right_value
        except:
            raise SemanticError(f'LessEqual-Operation is not defined between "{left_value}" and "{right_value}"')
        
        return less_equal_value, BooleanType()
#_________________________________________________________________________________________________________________________
#___________________________________________________Strings__________________________________________________________________
class ConcatNode(StringBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
    def evaluate(self, context: Context):
        left_value, _ = self.left.evaluate(context)
        right_value, _ = self.right.evaluate(context)
        concat_value = ''

        try:
            concat_value = left_value + right_value
        except:
            raise SemanticError(f'Concat-Operation is not defined between "{left_value}" and "{right_value}"')
        
        return concat_value, StringType()

class DoubleConcatNode(StringBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
    def evaluate(self, context: Context):
        left_value, _ = self.left.evaluate(context)
        right_value, _ = self.right.evaluate(context)
        double_concat_value = ''

        try:
            double_concat_value = left_value + ' ' + right_value
        except:
            raise SemanticError(f'DoubleConcat-Operation is not defined between "{left_value}" and "{right_value}"')
        
        return double_concat_value, StringType()
#_________________________________________________________________________________________________________________________
#__________________________________________________Arithmetic__________________________________________________________________

class PlusNode(ArithmeticBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
    def evaluate(self, context: Context):
        left_value, _ = self.left.evaluate(context)
        right_value, _ = self.right.evaluate(context)
        plus_value = 0

        try:
            plus_value = left_value + right_value
        except:
            raise SemanticError(f'Plus-Operation is not defined between "{left_value}" and "{right_value}"')
        
        return plus_value, NumberType()

class MinusNode(ArithmeticBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
    def evaluate(self, context: Context):
        left_value, _ = self.left.evaluate(context)
        right_value, _ = self.right.evaluate(context)
        minus_value = 0

        try:
            minus_value = left_value - right_value
        except:
            raise SemanticError(f'Minus-Operation is not defined between "{left_value}" and "{right_value}"')
        
        return minus_value, NumberType()

class MultNode(ArithmeticBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
    def evaluate(self, context: Context):
        left_value, _ = self.left.evaluate(context)
        right_value, _ = self.right.evaluate(context)
        mult_value = 0

        try:
            mult_value = left_value * right_value
        except:
            raise SemanticError(f'Mult-Operation is not defined between "{left_value}" and "{right_value}"')
        
        return mult_value, NumberType()

class DivNode(ArithmeticBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
    def evaluate(self, context: Context):
        left_value, _ = self.left.evaluate(context)
        right_value, _ = self.right.evaluate(context)
        div_value = 0

        if right_value == 0:
            raise SemanticError('Cannot divide for zero')
        try:
            div_value = left_value / right_value
        except:
            raise SemanticError(f'Div-Operation is not defined between "{left_value}" and "{right_value}"')
        
        return div_value, NumberType()

class ModNode(ArithmeticBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
    def evaluate(self, context: Context):
        left_value, _ = self.left.evaluate(context)
        right_value, _ = self.right.evaluate(context)
        mod_value = 0

        try:
            mod_value = left_value % right_value
        except:
            raise SemanticError(f'Mod-Operation is not defined between "{left_value}" and "{right_value}"')
        
        return mod_value, NumberType()

class PowNode(ArithmeticBinaryNode):
    def __init__(self, left, right):
        super().__init__(left, right)
    def evaluate(self, context: Context):
        left_value, _ = self.left.evaluate(context)
        right_value, _ = self.right.evaluate(context)
        pow_value = 0

        try:
            pow_value = left_value ^ right_value
        except:
            raise SemanticError(f'Pow-Operation is not defined between "{left_value}" and "{right_value}"')
        
        return pow_value, NumberType()

class PositiveNode(ArithmeticUnaryNode):
    def __init__(self, operand):
        super().__init__(operand)
    def evaluate(self, context: Context):
        operand_value, _ = self.operand.evaluate(context)
        positive_value = 0

        try:
            positive_value = +(operand_value)
        except:
            raise SemanticError(f'PositiveSign-Operation is not defined for "{operand_value}"')
        
        return positive_value, NumberType()

class NegativeNode(ArithmeticUnaryNode):
    def __init__(self, operand):
        super().__init__(operand)
    def evaluate(self, context: Context):
        operand_value, _ = self.operand.evaluate(context)
        negative_value = 0

        try:
            negative_value = -(operand_value)
        except:
            raise SemanticError(f'NegativeSign-Operation is not defined for "{operand_value}"')
        
        return negative_value, NumberType()


#_________________________________________________________________________________________________________________________
#__________________________________________________Literals__________________________________________________________________
class BooleanNode(LiteralNode):
    def __init__(self, lex):
        super().__init__(lex)
    def evaluate(self, context: Context):
        if self.lex == 'true':
            return True, BooleanType()
        elif self.lex == 'false':
            return False, BooleanType()
        else:
            raise SemanticError(f'"{self.lex}" is not a Boolean value')

class VarNode(LiteralNode):
    def __init__(self, lex):
        super().__init__(lex)
    def evaluate(self, context: Context):
        var = self.scope.find_variable(self.lex)
        var_value = var.value
        var_type = var.type
        
        if BooleanType() == var_type:
            if var_value == 'true':
                return True, BooleanType()
            elif var_value == 'false':
                return False, BooleanType()
            else:
                raise SemanticError(f'"{var_value}" is not a Boolean value')
        elif NumberType() == var_type:
            try:
                var_value = float(var_value)
            except:
                raise SemanticError(f'Cannot convert "{var_value}" to Number')
            else:
                return var_value, NumberType()
        elif StringType() == var_type:
            return var_value, var_type
        else:
            return var_type, var_type

class NumberNode(LiteralNode):
    def __init__(self, lex):
        super().__init__(lex)
    def evaluate(self, context: Context):
        number_value = 0
        try:
            number_value = float(self.lex)
        except:
            raise SemanticError(f'Cannot convert "{self.lex}" to Number')
        else:
            return number_value, NumberType()

class StringNode(LiteralNode):
    def __init__(self, lex):
        super().__init__(lex)
    def evaluate(self, context: Context):
        return self.lex, StringType()