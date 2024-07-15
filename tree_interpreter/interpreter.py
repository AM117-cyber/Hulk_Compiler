import cmp.nbpackage
import cmp.visitor as visitor
from grammar.hulk_grammar import G
from grammar.ast_nodes import *
from cmp.semantic import *
from cmp.errors import HulkRunTimeError
import math
import random

def sqrt_func(arg):
    if arg < 0:
        raise ValueError("sqrt is not defined for negative numbers")
    return math.sqrt(arg)

def log_func(arg, base):
    if arg <= 0 or base <= 0 or base == 1:
        raise ValueError("log is not defined for non-positive numbers or base <= 0 and base != 1")
    return math.log(arg, base)

def Print(x):
    if isinstance(x[0], str) or isinstance(x[0], float) or isinstance(x[0], bool):
        print(x[0])
        return x[0], x[1]
    else:
        print(f'Instance of {x[0].name}')
        return x[0], x[1]

built_in_func = {
    "range": lambda x: ([float(item) for item in range(int(x[0][0]), int(x[1][0]))], VectorType(NumberType())),
    "print": lambda x: (Print(*x)),
    "sqrt": lambda x: (sqrt_func(x[0][0]), NumberType()),
    "sin": lambda x: (math.sin(x[0][0]), NumberType()),
    "cos": lambda x:(math.cos(x[0][0]), NumberType()),
    "exp": lambda x: (math.exp(x[0][0]), NumberType()),
    "log": lambda x: (log_func(*[t[0] for t in reversed(x)]), NumberType()),
    "rand": lambda _: (random.random(), NumberType()),
    "parse": lambda x: (float(x[0][0]), NumberType()),
}


binary_operators = {
    "+": lambda x, y: (x[0] + y[0], NumberType()),
    "-": lambda x, y: (x[0] - y[0], NumberType()),
    "*": lambda x, y: (x[0] * y[0], NumberType()),
    "/": lambda x, y: (x[0] / y[0], NumberType()),
    "%": lambda x, y: (x[0] % y[0], NumberType()),
    "@": lambda x, y: (str(x[0]) + str(y[0]), StringType()),
    ">": lambda x, y: (x[0] > y[0], BooleanType()),
    "<": lambda x, y: (x[0] < y[0], BooleanType()),
    "|": lambda x, y: (x[0] or y[0], BooleanType()),
    "&": lambda x, y: (x[0] and y[0], BooleanType),
    "==": lambda x, y: (x[0] == y[0], BooleanType()),
    "!=": lambda x, y: (x[0] != y[0], BooleanType()),
    ">=": lambda x, y: (x[0] >= y[0], BooleanType()),
    "<=": lambda x, y: (x[0] <= y[0], BooleanType()),
    "**": lambda x, y: (x[0]**y[0], NumberType()),
    "@@": lambda x, y: (str(x[0]) + " " + str(y[0]), StringType()),
}

unary_operators = {"!": lambda x: (not x[0], BooleanType()), 
                   "-": lambda x: (-x[0], NumberType()),
                   "+": lambda x: (+x[0], NumberType())}

class Interpreter:
    def __init__(self,context,errors=[]):
        self.context = context
        self.errors = errors
        self.tuple_type_method = []

    @visitor.on('node')
    def visit(self, node):
        pass  

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode):
        return self.visit(node.expression)

    @visitor.when(VarDeclarationNode)
    def visit(self, node: VarDeclarationNode):
        node.scope.find_variable(node.name).set_value(self.visit(node.value)[0])

#_____________________________________________________________________________________________________________________________________
#__________________________________________Expressions______________________________________________________________________________________
        
    @visitor.when(ConditionalNode)
    def visit(self, node: ConditionalNode):
        for cond, expr in zip(node.conditions, node.expressions):
            if self.visit(cond)[0]:
                return self.visit(expr)
        return self.visit(node.default)

    
    @visitor.when(LetInNode)
    def visit(self, node: LetInNode):
        for var in node.variables:
            self.visit(var)
        return self.visit(node.body)
    
    @visitor.when(WhileNode)
    def visit(self, node: WhileNode):
        return_value = None
        return_type = None
        while self.visit(node.condition)[0]:
            return_value, return_type = self.visit(node.body)
        return return_value, return_type
    
    @visitor.when(ForNode)
    def visit(self, node: ForNode):
        item = node.scope.find_variable(node.item)
        iterable, iterable_type = self.visit(node.iterable)
        return_value = None
        return_type = None
        if isinstance(iterable,list):
            for it in iterable:
                item.set_value(it)
                return_value, return_type = self.visit(node.body)
        elif not iterable_type.conforms_to(self.context.get_protocol('Iterable')):
            error = HulkRunTimeError.NOT_CONFORMS_TO%(iterable.name,'Iterable')
            raise HulkRunTimeError(error,node.row,node.column)
        else:
            while self.visit(iterable.get_method('next').node.body)[0]:
                item.set_value(self.visit(iterable.get_method('current').node.body)[0])
                return_value, return_type = self.visit(node.body)
        return return_value, return_type
    
    @visitor.when(DestrNode)
    def visit(self, node: DestrNode):
        if isinstance(node.var, VarNode):
            var = node.scope.find_variable(node.var.lex)
            return_value, return_type = self.visit(node.expr)
            var.set_value(return_value)
        elif isinstance(node.var, CallTypeAttributeNode):
            att = self.tuple_type_method[-1][0].get_attribute(node.var.attribute)
            return_value, return_type = self.visit(node.expr)
            att.set_value(return_value)
        else:
            return None, None
        
        return return_value, return_type
    
    @visitor.when(CheckTypeNode)
    def visit(self, node: CheckTypeNode):
        value_left, left_type = self.visit(node.left)
        if isinstance(value_left, float):
            return NumberType().conforms_to(self.context.get_type(node.right))
        elif isinstance(value_left, bool):
            return BooleanType().conforms_to(self.context.get_type(node.right))
        elif isinstance(value_left, str):
            return StringType().conforms_to(self.context.get_type(node.right))
        else:
            return left_type.conforms_to(self.context.get_type(node.right)), BooleanType()
        
    @visitor.when(ExpressionBlockNode)
    def visit(self, node: ExpressionBlockNode):
        return_value = None
        return_type = None

        for expr in node.expressions:
            return_value, return_type = self.visit(expr)
        
        return return_value, return_type
    
    @visitor.when(CallFuncNode)
    def visit(self, node: CallFuncNode):
        if node.name == 'base' and len(node.arguments)==0 and len(self.tuple_type_method) != 0:
            base_method = self.tuple_type_method[-1][0].parent.get_method(self.tuple_type_method[-1][1].name)
            for base_param, current_param in zip(base_method.param_names, self.tuple_type_method[-1][1].param_names):
                current_param_var = self.tuple_type_method[-1][1].node.scope.find_variable(current_param)
                base_method.node.scope.find_variable(base_param).set_value(current_param_var.value)

            return self.visit(base_method.node.body)
        
        arguments = [self.visit(arg) for arg in node.arguments]
        
        if node.name in built_in_func:
            return built_in_func[node.name](tuple(arguments))
        function = self.context.get_function(node.name)
        #verificar tipos de los parámetros
        for param, (arg_value, arg_type) in zip(function.param_names, arguments):
            var = function.node.scope.find_variable(param)
            if not var.type.is_auto() and not var.type.is_error() and not var.type.conforms_to(arg_type):
                raise HulkRunTimeError(HulkRunTimeError.INVALID_TYPE_ARGUMENTS%(param, var.type.name, node.name,arg_type.name),node.row,node.column)
            var.set_value(arg_value)
        return self.visit(function.node.body)
    
    @visitor.when(TypeInstantiationNode)
    def visit(self, node: TypeInstantiationNode):
        arguments = [self.visit(arg) for arg in node.arguments]
        type = self.context.get_type(node.name)
        
        for param, (arg_value, arg_type) in zip(type.param_names, arguments):
            var = type.node.scope.find_variable(param)
            if not var.type.is_error() and not var.type.is_auto() and not var.type.conforms_to(arg_type):
                raise HulkRunTimeError(HulkRunTimeError.INVALID_TYPE_ARGUMENTS%(param, var.type.name, node.name,arg_type.name),node.row,node.column)
            var.set_value(arg_value)
        
        for param, parent_arg in zip(type.parent.param_names,type.node.parent_args):
            parent_param_var = type.parent.node.scope.find_variable(param)
            parent_arg_value, parent_arg_type = self.visit(parent_arg)
            if not parent_arg_type.is_error() and not parent_arg_type.is_auto() and not parent_arg_type.conforms_to(parent_param_var.type):
                raise HulkRunTimeError(HulkRunTimeError.INVALID_TYPE_ARGUMENTS%(param,parent_param_var.type.name,node.name, parent_arg_value.name))
            parent_param_var.set_value(parent_arg_value)

        for attribute in type.parent.attributes.values():
            attr_value, attr_type = self.visit(attribute.node)
            attribute.set_value(attr_value)

        for attribute in type.attributes.values():
            attr_value, attr_type = self.visit(attribute.node)
            attribute.set_value(attr_value)
        
        return type.node, type

    @visitor.when(TypeAttributeNode)
    def visit(self, node: TypeAttributeNode):
        return self.visit(node.value)
    
    @visitor.when(CallTypeAttributeNode)
    def visit(self, node: CallTypeAttributeNode):
        
        attr =  self.tuple_type_method[-1][0].get_attribute(node.attribute)
        return attr.value,attr.type


    @visitor.when(ExplicitVectorNode)
    def visit(self, node: ExplicitVectorNode):
        items_values = []
        current_type = None
        for item in node.items:
            value, item_type = self.visit(item)
            if current_type is not None and current_type != item_type:
                raise HulkRunTimeError(HulkRunTimeError.VECTOR_OBJECT_DIFFERENT_TYPES, node.row, node.column)
            current_type = item_type
            items_values.append(value)
        return items_values, VectorType(current_type)
    
    @visitor.when(ImplicitVectorNode)
    def visit(self, node: ImplicitVectorNode):
        item = node.scope.find_variable(node.item)
        iterable, iterable_type = self.visit(node.iterable)
        values = []
        if isinstance(iterable, list):
            return_type = None
            for it in iterable:
                item.set_value(it)
                value, return_type = self.visit(node.expr)
                values.append(value)
            return values, VectorType(return_type)
        else:
            if not iterable_type.conforms_to(self.context.get_protocol('Iterable')):
                error = HulkRunTimeError.NOT_CONFORMS_TO%(iterable_type.name,'Iterable')
                raise HulkRunTimeError(error, node.row, node.column)
            while self.visit(iterable_type.get_method('next').node.body)[0]:
                current_value, current_type = self.visit(iterable_type.get_method('current').node.body)
                item.set_value(current_value)
                values.append(self.visit(node.expr)[0])

            return values, VectorType(current_type)
    
    @visitor.when(IndexObjectNode)
    def visit(self, node: IndexObjectNode):
        obj, obj_type= self.visit(node.object)
        if not isinstance(obj, list):
            error = HulkRunTimeError.INVALID_INDEXING%(obj_type.name)
            raise HulkRunTimeError(error, node.row,node.column)
    
        size_object = len(obj)
        pos, pos_type = self.visit(node.pos)
        if NumberType() != pos_type:
            error = HulkRunTimeError.INVALID_INDEXING_OPERATION %(pos_type.name)
            raise HulkRunTimeError(error, node.row, node.column)
        if pos < 0 or pos > size_object-1:
            raise HulkRunTimeError('Index out of range',node.row,node.column)

        return obj[int(pos)],obj_type.get_method('current').return_type
    
    # copy_inst_value = inst_value.copy()
    @visitor.when(CallMethodNode)
    def visit(self, node: CallMethodNode):
        inst_value,inst_type = self.visit(node.inst_name)

        if isinstance(inst_value, list):
            # if isinstance(inst_type,VectorType):
            if node.method_name == 'next':
                if len(inst_value) == 0:
                    return False, BooleanType()
                return True, BooleanType()
            elif node.method_name == 'current':
                return inst_value.pop(0), inst_type.get_method('current').return_type
              
        method = inst_type.get_method(node.method_name)
        self.tuple_type_method.append((inst_type, method))
        arguments = [self.visit(arg) for arg in node.method_args]
        #verificar tipos de los parámetros
        for param, (arg_value, arg_type) in zip(method.param_names, arguments):
            var = method.node.scope.find_variable(param)
            if not var.type.is_error() and not var.type.is_auto() and not var.type.conforms_to(arg_type):
                raise HulkRunTimeError(HulkRunTimeError.INVALID_TYPE_ARGUMENTS%(param, var.type.name, node.name,arg_type.name),node.row,node.column)
            var.set_value(arg_value)
        return_value,return_type = self.visit(method.node.body)
        self.tuple_type_method.pop()
        return return_value,return_type

    
    @visitor.when(CastTypeNode)
    def visit(self, node: CastTypeNode):
        value_left, left_type = self.visit(node.left)
        if isinstance(value_left, float):
            return NumberType().conforms_to(self.context.get_type(node.right))
        elif isinstance(value_left, bool):
            return BooleanType().conforms_to(self.context.get_type(node.right))
        elif isinstance(value_left, str):
            return StringType().conforms_to(self.context.get_type(node.right))
        else:
            return self.context.get_type(node.right).conforms_to(left_type), BooleanType()
        
    @visitor.when(BinaryNode)
    def visit(self, node: BinaryNode):
        return binary_operators[node.operator](self.visit(node.left), self.visit(node.right))
    
    @visitor.when(UnaryNode)
    def visit(self, node: UnaryNode):
        return unary_operators[node.operator](self.visit(node.operand))
    
    @visitor.when(NumberNode)
    def visit(self, node: NumberNode):
        return float(node.lex), NumberType()
    
    @visitor.when(StringNode)
    def visit(self, node: StringNode):
        lex = node.lex.replace('\\"', '\"')
        lex = lex[1:len(lex)-1]
        return lex, StringType()
    
    @visitor.when(BooleanNode)
    def visit(self, node: BooleanNode):
        if node.lex == 'true':
            return True, BooleanType()
        elif node.lex == 'false':
            return False, BooleanType()
        else:
            return None, BooleanType()
        
    @visitor.when(VarNode)
    def visit(self, node: VarNode):
        var = node.scope.find_variable(node.lex)
        if var is None:
            if node.lex == 'self':
                return self.tuple_type_method[-1][0].node,self.tuple_type_method[-1][0]
        return var.value, var.type