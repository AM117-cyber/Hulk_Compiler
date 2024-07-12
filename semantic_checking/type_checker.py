import cmp.nbpackage
import cmp.visitor as visitor
from grammar.hulk_grammar import G
from grammar.ast_nodes import *
from cmp.semantic import *

WRONG_METHOD_RETURN_TYPE = 'Method "%s" in type "%s" has declared return type "%s" but returns "%s"'
WRONG_FUNCTION_RETURN_TYPE = 'Function "%s" return type is "%s" but it returns "%s"'
VARIABLE_IS_DEFINED = 'Variable "%s" is already defined in this scope'
WRONG_SIGNATURE = 'Method "%s" already defined in "%s" with a different signature.'
SELF_IS_READONLY = 'Variable "self" is read-only.'
LOCAL_ALREADY_DEFINED = 'Variable "%s" is already defined in method "%s".'
INCOMPATIBLE_TYPES = 'Cannot convert "%s" into "%s".'
VARIABLE_NOT_DEFINED = 'Variable "%s" is not defined in "%s".'
INVALID_OPERATION = 'Operation is not defined between "%s" and "%s".'
INVALID_IS_OPERATION = 'Invalid "IS" operation: "%s" is not a type'
INVALID_CAST_OPERATION = 'Cast operation is not defined between "%s" and "%s"'
INVALID_UNARY_OPERATION = 'Operation is not defined for "%s"'
VECTOR_OBJECT_DIFFERENT_TYPES = 'Vector is conformed by different types'
INVALID_INDEXING = 'Can not index into a "%s"'
INVALID_INDEXING_OPERATION = 'An index can not be a "%s"'
NOT_DEFINED = 'Variable "%s" is not defined'
INVALID_TYPE_ARGUMENTS = 'Type of param "%s" is "%s" in "%s" but it is being called with type "%s" '
INVALID_LEN_ARGUMENTS = '"%s" has %s parameters but it is being called with "%s" arguments'
PRIVATE_ATTRIBUTE = 'Cannot access attribute "%s" in type "%s" is private. All attributes are private'
NOT_CONFORMS_TO = '"%s" does not conform to "%s"'
INVALID_OVERRIDE = 'Method "%s" can not be overridden in class "%s".It is already defined in with a different signature.'


class TypeChecker:
    def __init__(self, context, errors=[]):
        self.context = context
        self.current_type = None
        self.current_method = None
        self.errors = errors

    @visitor.on('node')
    def visit(self, node, scope):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode, scope = Scope()):
        for declaration in node.declarations:
            try:
                self.visit(declaration, scope.create_child())
            except SemanticError as error:
                self.errors.append(error)

        self.current_type = None
        self.current_method = None
        self.visit(node.expression, scope)

#__________________________________________________________________________________________________________________
#__________________________________________Declarations__________________________________________________________________
    
    @visitor.when(TypeDeclarationNode)
    def visit(self, node: TypeDeclarationNode, scope: Scope):
        if(node.name in self.context.hulk_types):
            return
        self.current_type = self.context.get_type(node.name)
        if self.current_type.is_error():
            return
        
        if(len(self.current_type.param_types)>0):
            for name, type in zip(self.current_type.param_names, self.current_type.param_types):
                scope.define_variable(name, type, True)
            # child = scope.create_child()

            if not self.current_type.parent.is_error():
                parent_param_types = self.current_type.parent.param_types

                if len(node.parent_args) != len(parent_param_types):
                    self.errors.append(INVALID_LEN_ARGUMENTS%(self.current_type.parent.name,len(parent_param_types),len(node.parent_args)))
                    # return ErrorType()
                else:
                    for index,(param_type,arg) in enumerate(zip(parent_param_types,node.parent_args)):
                        arg_type = self.visit(arg, scope)
                        try:
                            param_type = self.assign_type(param_type,arg_type)
                            # if param_type.is_error():
                            #     return ErrorType()
                        except SemanticError:
                            self.errors.append(SemanticError(INVALID_TYPE_ARGUMENTS%(index, param_type.name ,arg_type.name))) 
                            # return ErrorType() 
        else:
            param_names, param_types = self.current_type.find_params()
            for param_name, param_type in zip(param_names,param_types):
                scope.define_variable(param_name,param_type, True)
            self.current_type.set_params(param_names,param_types)
            
            
        for attribute in node.attributes:
            try:
                self.visit(attribute, scope) 
            except SemanticError as error:
                self.errors.append(error)
        for method in node.methods:
            try:
                self.visit(method, scope.create_child()) 
            except SemanticError as error:
                self.errors.append(error)
        
    #Verificar que el atributo no lo tenga el padre
    @visitor.when(TypeAttributeNode)
    def visit(self, node: TypeAttributeNode, scope: Scope):
        self.current_method = None
        attribute: Attribute = self.current_type.get_attribute(node.name)
        expr_type = self.visit(node.value, scope)
        if(not attribute.is_error()):
            var_type = attribute.type
            try:
                var_type = self.assign_type(var_type,expr_type)
            except SemanticError: 
                self.errors.append(SemanticError(INCOMPATIBLE_TYPES%(expr_type.name,attribute.type.name)))
                # var_type = ErrorType()
            # scope.define_variable(node.name,var_type)
            else:
                attribute.set_type(var_type)
    

    @visitor.when(MethodDeclarationNode)
    def visit(self, node: MethodDeclarationNode, scope: Scope):
        self.current_method = self.current_type.get_method(node.name)
        try:
            parent_method = self.current_type.parent.get_method(node.name)
        except:
            pass
        else:
            if self.current_method != parent_method:
                self.errors.append(INVALID_OVERRIDE%(node.name,self.current_type.name))

        if self.current_method.is_error():
            return
        
        for name, type in zip(self.current_method.param_names, self.current_method.param_types):
            scope.define_variable(name, type, True)

        return_type = self.current_method.return_type

        expr_type = self.visit(node.body,scope)
        try:
            return_type = self.assign_type(return_type,expr_type)
        except:
            self.errors.append(WRONG_METHOD_RETURN_TYPE%(self.current_method.name,self.current_type.name,self.current_method.return_type.name,expr_type.name))
            # return_type = ErrorType()
        else:
            self.current_method.set_inferred_return_type(return_type)

    @visitor.when(FunctionDeclarationNode)
    def visit(self, node: FunctionDeclarationNode, scope: Scope):
        self.current_type = None
        if(node.name in self.context.hulk_functions):
            return
        self.current_method = self.context.get_function(node.name)
        if self.current_method.is_error():
            return
        
        for name, type in zip(self.current_method.param_names, self.current_method.param_types):
            scope.define_variable(name, type, True)

        return_type = self.current_method.return_type
        expr_type = self.visit(node.body,scope)

        try:
            return_type = self.assign_type(return_type,expr_type)
        except:
            self.errors.append(WRONG_FUNCTION_RETURN_TYPE%(self.current_method.name,self.current_method.return_type.name,expr_type.name))
            # return_type = ErrorType()
        else:
            self.current_method.set_inferred_return_type(return_type)


    @visitor.when(VarDeclarationNode)
    def visit(self, node: VarDeclarationNode, scope: Scope):
        if scope.is_local(node.name):
            self.errors.append(VARIABLE_IS_DEFINED%(node.name))
            # var = scope.find_variable(node.name)
            # var.set_type(ErrorType())
            #No sé si poner error a tomar que la única variable es la primera que se declaró
            return
        else:
            try:
                var_type = self.context.get_type_or_protocol(node.type) if node.type is not None else AutoType()
            except SemanticError as error:
                self.errors.append(error)
                var_type = ErrorType()
            else:
                expr_type = self.visit(node.value, scope)
                try:
                    var_type = self.assign_type(var_type,expr_type)
                except:
                    self.errors.append(INCOMPATIBLE_TYPES%(expr_type.name,var_type.name))
                    scope.define_variable(node.name,var_type)
                else:
                    scope.define_variable(node.name, var_type)

    def assign_type(self,var_type, expr_type):
        # if var_type.is_error() 
        # # or expr_type.is_error():
        #     return ErrorType()
        if var_type.is_auto():
            return expr_type
        elif not var_type.is_error() and not expr_type.is_error() and not expr_type.conforms_to(var_type):
            raise SemanticError('Error')
        else:
            return var_type
            
#_____________________________________________________________________________________________________________________________________
#__________________________________________Expressions______________________________________________________________________________________

    @visitor.when(ConditionalNode)
    def visit(self, node: ConditionalNode, scope: Scope):
        expressions = node.expressions +[node.default]

        for index,condition in enumerate(node.conditions):
            condition_type = self.visit(condition, scope)
            if not condition_type.is_error() and not condition_type.is_auto() and BooleanType() != condition_type:
                self.errors.append(SemanticError(INCOMPATIBLE_TYPES%(condition_type.name,'Boolean')))
            if condition == 'true':
                return self.visit(expressions[index], scope)
            
        types = [self.visit(expr,scope) for expr in expressions]
        return get_lowest_common_ancestor(types)
    
    @visitor.when(LetInNode)
    def visit(self, node: LetInNode, scope: Scope):
        for var_declaration in node.variables:
            scope = scope.create_child()
            self.visit(var_declaration,scope)
        return self.visit(node.body,scope)

    
    @visitor.when(WhileNode)
    def visit(self, node: WhileNode, scope: Scope):
        condition_type = self.visit(node.condition, scope)
        if BooleanType() != condition_type and not condition_type.is_auto() and not condition_type.is_error():
                self.errors.append(SemanticError(INCOMPATIBLE_TYPES%(condition_type.name, 'BooleanWhilee')))
            # return ErrorType()
            #No sé si retornar un error si el tipo de la condición no es booleano
        return self.visit(node.body,scope)


    


    @visitor.when(ForNode)
    def visit(self, node: ForNode, scope: Scope):
        child_scope = scope.create_child()
        iterable = self.visit(node.iterable,child_scope)
        
        if iterable.conforms_to(self.context.get_protocol('Iterable')): # marca mandarina (por que no conforma a iterable?) TE AMO TITI
            child_scope.define_variable(node.item, iterable.get_method('current').inferred_return_type)
        elif not iterable.is_auto() and not iterable.is_error():
            self.errors.append(NOT_CONFORMS_TO%(iterable.name,'Iterable'))
        else:
            child_scope.define_variable(node.item,iterable) # marca mandarina (definir node.item cuando entra en el elif)

        body_type = self.visit(node.body, child_scope)
        return body_type

    @visitor.when(DestrNode)
    def visit(self, node: DestrNode, scope: Scope):
        
        var_type = self.visit(node.var, scope) # marca mandarina (node.var es un string y no un nodo, problema en la gramatica, creo)
        if var_type.is_error():
            return var_type
        
        expr_type = self.visit(node.expr, scope)
        if self.current_type is not None and self.current_method is not None and var_type == self.current_type: # marca mandarina
            self.errors.append(SemanticError(SELF_IS_READONLY))
            return ErrorType()
        if expr_type.is_error():
            return var_type
        if not expr_type.conforms_to(var_type):
            self.errors.append(SemanticError(INCOMPATIBLE_TYPES%(expr_type.name,var_type.name)))
        return var_type

#_________________________________________________________________________________________________________________________
#________________________________________________Binary__________________________________________________________________

    @visitor.when(EqualityBinaryNode)
    def visit(self, node:EqualityBinaryNode, scope: Scope):
        left_type = self.visit(node.left, scope)
        right_type = self.visit(node.right, scope)

        if left_type.is_error() or right_type.is_error():
            return BooleanType()
        
        if BooleanType() == left_type == right_type or \
            NumberType() == left_type == right_type or \
            AutoType() == left_type == right_type or \
            left_type.is_auto() and NumberType() == right_type or \
            NumberType() == left_type and right_type.is_auto() or \
            BooleanType() == left_type and right_type.is_auto() or \
            left_type.is_auto() and BooleanType() ==right_type:
            return BooleanType()
        self.errors(SemanticError(INVALID_OPERATION(left_type.name,right_type.name)))
        return BooleanType()
    
    @visitor.when(ComparisonBinaryNode)
    def visit(self, node:ComparisonBinaryNode, scope: Scope):
        left_type = self.visit(node.left, scope)
        right_type = self.visit(node.right, scope)

        if left_type.is_error() or right_type.is_error():
            return BooleanType()
        if NumberType() == left_type == right_type or\
            AutoType() == left_type == right_type or\
            left_type.is_auto and NumberType() == right_type or\
            NumberType() == left_type and right_type.is_auto():
            return BooleanType()
        elif left_type.is_auto():
            left_type = NumberType()
        elif right_type.is_auto():
            right_type = NumberType()
        self.errors(SemanticError(INVALID_OPERATION(left_type,right_type)))
        return BooleanType()
    
    @visitor.when(ArithmeticBinaryNode)
    def visit(self, node: ArithmeticBinaryNode, scope: Scope):
        left_type = self.visit(node.left, scope)
        right_type = self.visit(node.right, scope)

        if (NumberType() == left_type or left_type.is_auto()) and (NumberType() == right_type or right_type.is_auto()):
            return NumberType()
        elif left_type.is_error() or right_type.is_error():
            return NumberType()
        
        self.errors.append(SemanticError(INVALID_OPERATION%(left_type.name, right_type.name)))
        return NumberType()
    
    @visitor.when(BooleanBinaryNode)
    def visit(self, node: BooleanBinaryNode, scope: Scope):
        left_type = self.visit(node.left, scope)
        right_type = self.visit(node.right, scope)

        if (BooleanType() == left_type or left_type.is_auto()) and (BooleanType() == right_type or right_type.is_auto()):
            return BooleanType()
        elif left_type.is_error() or right_type.is_error():
            return BooleanType()
        
        self.errors.append(SemanticError(INVALID_OPERATION%(left_type.name, right_type.name)))
        return BooleanType()
    

    @visitor.when(CheckTypeNode)
    def visit(self, node:CheckTypeNode, scope: Scope):
        #no estoy segura de si esto puede pasar
        if self.visit(node.left, scope).is_error():
            return BooleanType()
        try:
            self.context.get_type_or_protocol(node.right) 
        except SemanticError as error:
            self.errors.append(SemanticError(INVALID_IS_OPERATION%(node.right)))
        return BooleanType()
    
    @visitor.when(StringBinaryNode)
    def visit(self, node:StringBinaryNode, scope:Scope):
        left_type = self.visit(node.left, scope)
        right_type = self.visit(node.right, scope)
        if left_type not in [StringType(),BooleanType(),NumberType(), AutoType(), ErrorType()] or right_type not in [StringType(),BooleanType(),NumberType(), AutoType(), ErrorType()]:
            self.errors.append(INVALID_OPERATION%(left_type.name,right_type.name))
        return StringType()

#_________________________________________________________________________________________________________________________
#_________________________________________________Atoms__________________________________________________________________
    
    @visitor.when(ExpressionBlockNode)
    def visit(self, node:ExpressionBlockNode, scope: Scope):
        scope = scope.create_child()

        for expr in node.expressions:
            type = self.visit(expr,scope)
        return type

    @visitor.when(CallFuncNode)
    def visit(self, node:CallFuncNode, scope: Scope):
        if node.name == 'base' and len(node.arguments)==0 and self.current_type is not None and self.current_method is not None:
            return self.current_method.inferred_return_type
        try:
            function = self.context.get_function(node.name)
        except SemanticError as error:
            self.errors.append(error)
            return ErrorType()
        if function.is_error() or function.return_type.is_error():
            return ErrorType()
        if len(function.param_types) != len(node.arguments):
            self.errors.append(INVALID_LEN_ARGUMENTS%(function.name,len(function.param_types),len(node.arguments)))
            return ErrorType()
        else:
            for index,(param_type,arg) in enumerate(zip(function.param_types,node.arguments)):
                arg_type = self.visit(arg, scope)
                try:
                    param_type = self.assign_type(param_type,arg_type)
                    # if param_type.is_error():
                    #     return ErrorType()
                except SemanticError:
                    self.errors.append(SemanticError(INVALID_TYPE_ARGUMENTS%(function.param_names[index], function.param_types[index].name,function.name,arg_type.name))) 
                    # return ErrorType() 
        if function.name == 'print':
            return arg_type
        return function.inferred_return_type

    @visitor.when(TypeInstantiationNode)
    def visit(self, node: TypeInstantiationNode, scope: Scope):
        # for argument in node.arguments:
        #     if ErrorType() == self.visit(argument, scope):
        #         return ErrorType()
        try:
            type= self.context.get_type(node.name)
        except SemanticError as error:
            self.errors.append(SemanticError(error))
            return ErrorType()  

        param_types = type.param_types
        if len(node.arguments) != len(param_types):
            self.errors.append(INVALID_LEN_ARGUMENTS%(type.name,len(type.param_types),len(node.arguments)))
            # return ErrorType()
        else:
            for index, (param_type, arg) in enumerate(zip(param_types, node.arguments)):
                arg_type = self.visit(arg, scope)
                try:
                    param_type = self.assign_type(param_type,arg_type)
                    # if param_type.is_error():
                    #     return ErrorType()
                except SemanticError:
                    self.errors.append(SemanticError(INVALID_TYPE_ARGUMENTS%(type.param_names[index], param_type.name,type.name,arg_type.name))) 
                    # return ErrorType() 
        return type

    @visitor.when(ExplicitVectorNode)
    def visit(self, node: ExplicitVectorNode, scope: Scope):
        items_type = [self.visit(item, scope) for item in node.items]
        try:
            iterable_type = get_vector_type(items_type)
        except:
            self.errors.append(SemanticError(VECTOR_OBJECT_DIFFERENT_TYPES))
            return ErrorType()
        #OJO No sé si retornar ErrorType()
        return VectorType(iterable_type)
    
    # changed 
    @visitor.when(ImplicitVectorNode)
    def visit(self, node: ImplicitVectorNode, scope: Scope):
        child_scope = scope.create_child()
        iterable = self.visit(node.iterable,child_scope)
        
        if iterable.conforms_to(self.context.get_protocol('Iterable')):
            child_scope.define_variable(node.item, iterable.get_method('current').inferred_return_type)
        elif not iterable.is_auto() and not iterable.is_error():
            self.errors.append(NOT_CONFORMS_TO%(iterable.name,'Iterable'))
        else:
            child_scope.define_variable(node.item,iterable)
        expr_type = self.visit(node.expr, child_scope)
        return VectorType(expr_type)

    
    @visitor.when(IndexObjectNode)
    def visit(self, node: IndexObjectNode, scope: Scope):
        pos_type = self.visit(node.pos, scope)
        if NumberType() != pos_type and not pos_type.is_auto() and not pos_type.is_error():
            self.errors.append(INVALID_INDEXING_OPERATION%(pos_type))
            # return ErrorType()
        
        object_type = self.visit(node.object, scope)
        if object_type.is_error():
            return ErrorType()
        elif not object_type.conforms_to(self.context.get_protocol('Iterable')):
            self.errors.append(INVALID_INDEXING%(object_type.name))
            # return ErrorType()
        # else:
        return object_type.get_method('current').inferred_return_type

    @visitor.when(CallMethodNode)
    def visit(self, node:CallMethodNode, scope: Scope):
        owner = self.visit(node.inst_name, scope)
        if owner.is_error():
            return ErrorType()
        try:
            method = owner.get_method(node.method_name)
        except SemanticError as error:
            self.errors.append(SemanticError(error))
            return ErrorType()
        if method.is_error():
            return ErrorType()
        if len(method.param_types) != len(node.method_args):
            self.errors.append(INVALID_LEN_ARGUMENTS%(method.method_name,len(method.param_types),len(node.method_args)))
            # return ErrorType()
        else:
            for index, (param_type, arg) in enumerate(zip(method.param_types,node.method_args)):
                arg_type = self.visit(arg,scope)
                try:
                    self.assign_type(param_type,arg_type)
                    # if param_type.is_error():
                    #     return ErrorType()
                except SemanticError:
                    self.errors.append(SemanticError(INVALID_TYPE_ARGUMENTS%(method.param_names[index], method.param_types[index].name,arg_type.name))) 
                    # return ErrorType()
        return method.inferred_return_type

    @visitor.when(CallTypeAttributeNode)
    def visit(self, node:CallTypeAttributeNode, scope: Scope):
        owner = self.visit(node.inst_name, scope)
        if owner.is_error():
            return ErrorType()
        if owner != self.current_type:
            self.errors.append(SemanticError(PRIVATE_ATTRIBUTE%(node.attribute, owner.name)))
            return ErrorType()
        try:
            attribute = owner.get_attribute(node.attribute)
        except SemanticError as error:
            self.errors.append(SemanticError(error))
            return ErrorType()
        else:
            return attribute.type
        
    
    
    @visitor.when(CastTypeNode)
    def visit(self, node:CastTypeNode, scope: Scope):
        inst_type = self.visit(node.inst_name, scope)
        if inst_type.is_error():
            return ErrorType()
        
        if isinstance(inst_type,Type):
            try:
                type_cast = self.context.get_type(node.type_cast)
            except SemanticError as error:
                self.errors.append(SemanticError(error))
                return ErrorType()
            else:
                if not type_cast.conforms_to(inst_type):
                    self.errors.append(SemanticError(NOT_CONFORMS_TO%(type_cast.name,inst_type.name)+INVALID_CAST_OPERATION%(inst_type.name,type_cast.name)))
        else:
            try:
                type_cast = self.context.get_type_or_protocol(node.type_cast)
            except SemanticError as error:
                self.errors.append(SemanticError(error))
                return ErrorType()
            else:
                if not type_cast.conforms_to(inst_type):
                    self.errors.append(SemanticError(NOT_CONFORMS_TO%(type_cast.name,inst_type.name)+INVALID_CAST_OPERATION%(inst_type.name,type_cast.name)))
        #No sé si retornar error o type_cast
        return type_cast

#_________________________________________________________________________________________________________________________
#_________________________________________________Unary__________________________________________________________________
    
    @visitor.when(ArithmeticUnaryNode)
    def visit(self, node: ArithmeticUnaryNode, scope: Scope):
        operand_type = self.visit(node.operand, scope)

        if NumberType() == operand_type or operand_type.is_auto():
            return NumberType()
        elif not operand_type.is_error():
            self.errors.append(SemanticError(INVALID_UNARY_OPERATION%(operand_type.name)))
        return NumberType()

    
    @visitor.when(BooleanUnaryNode)
    def visit(self, node: BooleanUnaryNode, scope: Scope):
        operand_type = self.visit(node.operand, scope)

        if BooleanType() == operand_type or operand_type.is_auto():
            return BooleanType()
        elif not operand_type.is_error():
            self.errors.append(SemanticError(INVALID_UNARY_OPERATION%(operand_type.name)))
        return BooleanType()
    

#_________________________________________________________________________________________________________________________
#__________________________________________________Literals__________________________________________________________________

    @visitor.when(BooleanNode)
    def visit(self, node: BooleanNode, scope: Scope):
        return BooleanType()

    @visitor.when(StringNode)
    def visit(self, node: StringNode, scope: Scope):
        return StringType()

    @visitor.when(NumberNode)
    def visit(self, node: NumberNode, scope: Scope):
        return NumberType()
    

    @visitor.when(VarNode)
    def visit(self, node: VarNode, scope: Scope):

        var = scope.find_variable(node.lex)
        if var is None:
            if node.lex == 'self':
                if(self.current_type is not None and self.current_method is not None):
                    return self.current_type
                else:
                    self.errors.append('"self" is not defined in this context')
                    return ErrorType()
            else:
                self.errors.append(SemanticError(NOT_DEFINED%(node.lex)))
                return ErrorType()
        else:
            return var.type 


        
    


         


