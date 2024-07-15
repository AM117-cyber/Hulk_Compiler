import cmp.nbpackage
import cmp.visitor as visitor
from grammar.hulk_grammar import G
from grammar.ast_nodes import *
from cmp.semantic import *
from cmp.errors import HulkSemanticError
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
        node.scope = scope
        for declaration in node.declarations:
            try:
                self.visit(declaration, node.scope.create_child())
            except SemanticError as error:
                self.errors.append(error)

        self.current_type = None
        self.current_method = None
        self.visit(node.expression, node.scope)

#__________________________________________________________________________________________________________________
#__________________________________________Declarations__________________________________________________________________
    
    @visitor.when(TypeDeclarationNode)
    def visit(self, node: TypeDeclarationNode, scope: Scope):
        node.scope = scope
        if(node.name in self.context.hulk_types):
            return
        self.current_type = self.context.get_type(node.name)
        if self.current_type.is_error():
            return
        
        if len(self.current_type.param_types)>0:
            for name, type in zip(self.current_type.param_names, self.current_type.param_types):
                node.scope.define_variable(name, type, True)
            # child = scope.create_child()

            if not self.current_type.parent.is_error():
                parent_param_types = self.current_type.parent.param_types

                if len(node.parent_args) != len(parent_param_types):
                    error = HulkSemanticError.INVALID_LEN_ARGUMENTS%(self.current_type.parent.name,len(parent_param_types),len(node.parent_args))
                    self.errors.append(HulkSemanticError(error,node.row,node.column))
                    # return ErrorType()
                else:
                    for index,(param_type,arg) in enumerate(zip(parent_param_types,node.parent_args)):
                        arg_type = self.visit(arg, node.scope)
                        try:
                            param_type = self.assign_type(param_type,arg_type)
                            # if param_type.is_error():
                            #     return ErrorType()
                        except SemanticError:
                            error = HulkSemanticError.INVALID_TYPE_ARGUMENTS%(index, param_type.name ,arg_type.name)
                            self.errors.append(HulkSemanticError(error,node.row,node.column)) 
                            # return ErrorType() 
        else:
            param_names, param_types = self.current_type.find_params()
            for param_name, param_type in zip(param_names,param_types):
                node.scope.define_variable(param_name,param_type, True)
            self.current_type.set_params(param_names,param_types)
            node.parent_args = [VarNode(param) for param in param_names]
            for arg in node.parent_args:
                arg.scope = node.scope
            
        for attribute in node.attributes:
            try:
                self.visit(attribute, node.scope) 
            except SemanticError as error:
                self.errors.append(HulkSemanticError(error,node.row,node.column)) 
        for method in node.methods:
            try:
                self.visit(method, node.scope.create_child()) 
            except SemanticError as error:
                self.errors.append(HulkSemanticError(error,node.row,node.column))
        
    #Verificar que el atributo no lo tenga el padre
    @visitor.when(TypeAttributeNode)
    def visit(self, node: TypeAttributeNode, scope: Scope):
        node.scope = scope
        self.current_method = None
        attribute: Attribute = self.current_type.get_attribute(node.name)
        expr_type = self.visit(node.value, node.scope)
        if not attribute.is_error():
            var_type = attribute.type
            try:
                var_type = self.assign_type(var_type,expr_type)
            except SemanticError: 
                error = HulkSemanticError.INCOMPATIBLE_TYPES%(expr_type.name,attribute.type.name)
                self.errors.append(HulkSemanticError(error,node.row,node.column))
                # var_type = ErrorType()
            # scope.define_variable(node.name,var_type)
            else:
                attribute.set_type(var_type)
    

    @visitor.when(MethodDeclarationNode)
    def visit(self, node: MethodDeclarationNode, scope: Scope):
        node.scope = scope
        self.current_method = self.current_type.get_method(node.name)
        try:
            parent_method = self.current_type.parent.get_method(node.name)
        except:
            pass
        else:
            if self.current_method != parent_method:
                error = HulkSemanticError.INVALID_OVERRIDE%(node.name,self.current_type.name)
                self.errors.append(HulkSemanticError(error,node.row,node.column))


        if self.current_method.is_error():
            return
        
        for name, type in zip(self.current_method.param_names, self.current_method.param_types):
            node.scope.define_variable(name, type, True)

        return_type = self.current_method.return_type

        expr_type = self.visit(node.body,node.scope)
        try:
            return_type = self.assign_type(return_type,expr_type)
        except:
            error = HulkSemanticError.WRONG_METHOD_RETURN_TYPE%(self.current_method.name,self.current_type.name,self.current_method.return_type.name,expr_type.name)
            self.errors.append(HulkSemanticError(error,node.row,node.column))
            
            # return_type = ErrorType()
        else:
            self.current_method.set_inferred_return_type(return_type)

    @visitor.when(FunctionDeclarationNode)
    def visit(self, node: FunctionDeclarationNode, scope: Scope):
        self.current_type = None
        node.scope = scope
        if(node.name in self.context.hulk_functions):
            return
        self.current_method = self.context.get_function(node.name)
        if self.current_method.is_error():
            return
        
        for name, type in zip(self.current_method.param_names, self.current_method.param_types):
            node.scope.define_variable(name, type, True)

        return_type = self.current_method.return_type
        expr_type = self.visit(node.body,node.scope)

        try:
            return_type = self.assign_type(return_type,expr_type)
        except:
            error = HulkSemanticError.WRONG_FUNCTION_RETURN_TYPE%(self.current_method.name,self.current_method.return_type.name,expr_type.name)
            self.errors.append(HulkSemanticError(error,node.row,node.column))
            
            # return_type = ErrorType()
        else:
            self.current_method.set_inferred_return_type(return_type)


    @visitor.when(VarDeclarationNode)
    def visit(self, node: VarDeclarationNode, scope: Scope):
        node.scope = scope
        if node.scope.is_local(node.name):
            error = HulkSemanticError.VARIABLE_IS_DEFINED%(node.name)
            self.errors.append(HulkSemanticError(error,node.row,node.column))

            # var = scope.find_variable(node.name)
            # var.set_type(ErrorType())
            #No sé si poner error a tomar que la única variable es la primera que se declaró
            return
        else:
            try:
                var_type = self.context.get_type_or_protocol(node.type) if node.type is not None else AutoType()
            except SemanticError as error:
                self.errors.append(HulkSemanticError(error,node.row,node.column))
                var_type = ErrorType()
            else:
                expr_type = self.visit(node.value, node.scope)
                try:
                    var_type = self.assign_type(var_type,expr_type)
                except:
                    error = HulkSemanticError.INCOMPATIBLE_TYPES%(expr_type.name,var_type.name)
                    self.errors.append(HulkSemanticError(error,node.row,node.column))
                    node.scope.define_variable(node.name,var_type)
                else:
                    node.scope.define_variable(node.name, var_type)

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
        node.scope = scope
        expressions = node.expressions +[node.default]

        for index,condition in enumerate(node.conditions):
            condition_type = self.visit(condition, node.scope)
            if not condition_type.is_error() and not condition_type.is_auto() and BooleanType() != condition_type:
                error = HulkSemanticError.INCOMPATIBLE_TYPES%(condition_type.name,'Boolean')
                self.errors.append(HulkSemanticError(error,node.row,node.column))
            if condition == 'true':
                return self.visit(expressions[index], node.scope)
            
        types = [self.visit(expr,node.scope) for expr in expressions]
        return get_lowest_common_ancestor(types)
    
    @visitor.when(LetInNode)
    def visit(self, node: LetInNode, scope: Scope):
        node.scope = scope
        for var_declaration in node.variables:
            scope = scope.create_child()
            self.visit(var_declaration,scope)
        return self.visit(node.body,scope)

    
    @visitor.when(WhileNode)
    def visit(self, node: WhileNode, scope: Scope):
        node.scope = scope
        condition_type = self.visit(node.condition, node.scope)
        if BooleanType() != condition_type and not condition_type.is_auto() and not condition_type.is_error():
                error = HulkSemanticError.INCOMPATIBLE_TYPES%(condition_type.name, 'Boolean')
                self.errors.append(HulkSemanticError(error,node.row,node.column))
            # return ErrorType()
            #No sé si retornar un error si el tipo de la condición no es booleano
        return self.visit(node.body,node.scope)


    


    @visitor.when(ForNode)
    def visit(self, node: ForNode, scope: Scope):
        node.scope = scope.create_child()
        iterable = self.visit(node.iterable,node.scope)
        
        if iterable.conforms_to(self.context.get_protocol('Iterable')): 
            node.scope.define_variable(node.item, iterable.get_method('current').inferred_return_type)
        elif not iterable.is_auto() and not iterable.is_error():
            error = HulkSemanticError.NOT_CONFORMS_TO%(iterable.name,'Iterable')
            self.errors.append(HulkSemanticError(error,node.row,node.column))
        else:
            node.scope.define_variable(node.item,iterable) # marca mandarina (definir node.item cuando entra en el elif)

        body_type = self.visit(node.body, node.scope)
        return body_type

    @visitor.when(DestrNode)
    def visit(self, node: DestrNode, scope: Scope):
        node.scope = scope
        var_type = self.visit(node.var, node.scope) # marca mandarina (node.var es un string y no un nodo, problema en la gramatica, creo)
        
        expr_type = self.visit(node.expr, node.scope)
        if var_type.is_error():
            return var_type
        if self.current_type is not None and self.current_method is not None and var_type == self.current_type: 
            error = HulkSemanticError.SELF_IS_READONLY
            self.errors.append(HulkSemanticError(error,node.row,node.column))
            return ErrorType()
        if expr_type.is_error():
            return var_type
        if not expr_type.conforms_to(var_type):
            error = HulkSemanticError.INCOMPATIBLE_TYPES%(expr_type.name,var_type.name)
            self.errors.append(HulkSemanticError(error,node.row,node.column))
        return var_type

#_________________________________________________________________________________________________________________________
#________________________________________________Binary__________________________________________________________________

    @visitor.when(EqualityBinaryNode)
    def visit(self, node:EqualityBinaryNode, scope: Scope):
        node.scope = scope
        left_type = self.visit(node.left, node.scope)
        right_type = self.visit(node.right, node.scope)

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
        error = HulkSemanticError.INVALID_OPERATION(left_type.name,right_type.name)
        self.errors.append(HulkSemanticError(error,node.row,node.column))
        return BooleanType()
    
    @visitor.when(ComparisonBinaryNode)
    def visit(self, node:ComparisonBinaryNode, scope: Scope):
        node.scope = scope
        left_type = self.visit(node.left, node.scope)
        right_type = self.visit(node.right, node.scope)

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
        error = HulkSemanticError.INVALID_OPERATION(left_type,right_type)
        self.errors.append(HulkSemanticError(error,node.row,node.column))
        return BooleanType()
    
    @visitor.when(ArithmeticBinaryNode)
    def visit(self, node: ArithmeticBinaryNode, scope: Scope):
        node.scope = scope
        left_type = self.visit(node.left, node.scope)
        right_type = self.visit(node.right, node.scope)

        if (NumberType() == left_type or left_type.is_auto()) and (NumberType() == right_type or right_type.is_auto()):
            return NumberType()
        elif left_type.is_error() or right_type.is_error():
            return NumberType()
        
        error = HulkSemanticError.INVALID_OPERATION%(left_type.name, right_type.name)
        self.errors.append(HulkSemanticError(error,node.row,node.column))
        return NumberType()
    
    @visitor.when(BooleanBinaryNode)
    def visit(self, node: BooleanBinaryNode, scope: Scope):
        node.scope = scope
        left_type = self.visit(node.left, node.scope)
        right_type = self.visit(node.right, node.scope)

        if (BooleanType() == left_type or left_type.is_auto()) and (BooleanType() == right_type or right_type.is_auto()):
            return BooleanType()
        elif left_type.is_error() or right_type.is_error():
            return BooleanType()
        
        error = HulkSemanticError.INVALID_OPERATION%(left_type.name, right_type.name)
        self.errors.append(HulkSemanticError(error,node.row,node.column))
        return BooleanType()
    

    @visitor.when(CheckTypeNode)
    def visit(self, node:CheckTypeNode, scope: Scope):
        node.scope = scope
        #no estoy segura de si esto puede pasar
        if self.visit(node.left, node.scope).is_error():
            return BooleanType()
        try:
            self.context.get_type_or_protocol(node.right) 
        except SemanticError as error:
            error = HulkSemanticError.INVALID_IS_OPERATION%(node.right)
            self.errors.append(HulkSemanticError(error,node.row,node.column))
        return BooleanType()
    
    @visitor.when(StringBinaryNode)
    def visit(self, node:StringBinaryNode, scope:Scope):
        node.scope = scope
        left_type = self.visit(node.left, node.scope)
        right_type = self.visit(node.right, node.scope)
        if left_type not in [StringType(),BooleanType(),NumberType(), AutoType(), ErrorType()] or right_type not in [StringType(),BooleanType(),NumberType(), AutoType(), ErrorType()]:
            error = HulkSemanticError.INVALID_OPERATION%(left_type.name,right_type.name)
            self.errors.append(HulkSemanticError(error,node.row,node.column))
        return StringType()

#_________________________________________________________________________________________________________________________
#_________________________________________________Atoms__________________________________________________________________
    
    @visitor.when(ExpressionBlockNode)
    def visit(self, node:ExpressionBlockNode, scope: Scope):
        node.scope = scope.create_child()

        for expr in node.expressions:
            type = self.visit(expr,node.scope)
        return type

    @visitor.when(CallFuncNode)
    def visit(self, node:CallFuncNode, scope: Scope):
        node.scope = scope
        if node.name == 'base' and len(node.arguments)==0 and self.current_type is not None and self.current_method is not None:
            try:
                parent_method = self.current_type.parent.get_method(self.current_method.name)
            except SemanticError as error:
                self.errors.append(HulkSemanticError(error, node.row,node.column))
                return ErrorType()
            return parent_method.inferred_return_type
        try:
            function = self.context.get_function(node.name)
        except SemanticError as error:
            self.errors.append(HulkSemanticError(error,node.row,node.column))
            return ErrorType()
        if function.is_error() or function.return_type.is_error():
            return ErrorType()
        if len(function.param_types) != len(node.arguments):
            error = HulkSemanticError.INVALID_LEN_ARGUMENTS%(function.name,len(function.param_types),len(node.arguments))
            self.errors.append(HulkSemanticError(error,node.row,node.column))
            return ErrorType()
        else:
            for index,(param_type,arg) in enumerate(zip(function.param_types,node.arguments)):
                arg_type = self.visit(arg, node.scope)
                try:
                    param_type = self.assign_type(param_type,arg_type)
                    # if param_type.is_error():
                    #     return ErrorType()
                except SemanticError:
                    error = HulkSemanticError.INVALID_TYPE_ARGUMENTS%(function.param_names[index], function.param_types[index].name,function.name,arg_type.name)
                    self.errors.append(HulkSemanticError(error,node.row,node.column))
                    # return ErrorType() 
        if function.name == 'print':
            return arg_type
        return function.inferred_return_type

    @visitor.when(TypeInstantiationNode)
    def visit(self, node: TypeInstantiationNode, scope: Scope):
        node.scope = scope
        # for argument in node.arguments:
        #     if ErrorType() == self.visit(argument, scope):
        #         return ErrorType()
        try:
            type= self.context.get_type(node.name)
        except SemanticError as error:
            self.errors.append(HulkSemanticError(error,node.row,node.column))
            return ErrorType()  

        param_types = type.param_types
        if len(node.arguments) != len(param_types):
            error = HulkSemanticError.INVALID_LEN_ARGUMENTS%(type.name,len(type.param_types),len(node.arguments))
            self.errors.append(HulkSemanticError(error,node.row,node.column))
            # return ErrorType()
        else:
            for index, (param_type, arg) in enumerate(zip(param_types, node.arguments)):
                arg_type = self.visit(arg, node.scope)
                try:
                    param_type = self.assign_type(param_type,arg_type)
                    # if param_type.is_error():
                    #     return ErrorType()
                except SemanticError:
                    error = HulkSemanticError.INVALID_TYPE_ARGUMENTS%(type.param_names[index], param_type.name,type.name,arg_type.name)
                    self.errors.append(HulkSemanticError(error,node.row,node.column))
                    # return ErrorType() 
        return type

    @visitor.when(ExplicitVectorNode)
    def visit(self, node: ExplicitVectorNode, scope: Scope):
        node.scope = scope
        items_type = [self.visit(item, node.scope) for item in node.items]
        try:
            iterable_type = get_vector_type(items_type)
        except:
            error = HulkSemanticError.VECTOR_OBJECT_DIFFERENT_TYPES
            self.errors.append(HulkSemanticError(error,node.row,node.column))
            return ErrorType()
        #OJO No sé si retornar ErrorType()
        return VectorType(iterable_type)
    
    # changed 
    @visitor.when(ImplicitVectorNode)
    def visit(self, node: ImplicitVectorNode, scope: Scope):
        node.scope = scope.create_child()
        iterable = self.visit(node.iterable,node.scope)
        
        if iterable.conforms_to(self.context.get_protocol('Iterable')):
            node.scope.define_variable(node.item, iterable.get_method('current').inferred_return_type)
        elif not iterable.is_auto() and not iterable.is_error():
            error = HulkSemanticError.NOT_CONFORMS_TO%(iterable.name,'Iterable')
            self.errors.append(HulkSemanticError(error,node.row,node.column))
        else:
            node.scope.define_variable(node.item,iterable)
        expr_type = self.visit(node.expr, node.scope)
        return VectorType(expr_type)

    
    @visitor.when(IndexObjectNode)
    def visit(self, node: IndexObjectNode, scope: Scope):
        node.scope = scope
        pos_type = self.visit(node.pos, node.scope)
        if NumberType() != pos_type and not pos_type.is_auto() and not pos_type.is_error():
            error = HulkSemanticError.INVALID_INDEXING_OPERATION%(pos_type)
            self.errors.append(HulkSemanticError(error,node.row,node.column))
            # return ErrorType()
        
        object_type = self.visit(node.object, node.scope)
        if object_type.is_error():
            return ErrorType()
        # elif not object_type.conforms_to(self.context.get_protocol('Iterable')):
        elif not isinstance(object_type,VectorType):
            error = HulkSemanticError.INVALID_INDEXING%(object_type.name)
            self.errors.append(HulkSemanticError(error,node.row,node.column))
            # return ErrorType()
        # else:
        return object_type.get_method('current').inferred_return_type

    @visitor.when(CallMethodNode)
    def visit(self, node:CallMethodNode, scope: Scope):
        node.scope = scope
        owner = self.visit(node.inst_name, node.scope)
        if owner.is_error():
            return ErrorType()
        try:
            method = owner.get_method(node.method_name)
        except SemanticError as error:
            self.errors.append(HulkSemanticError(error,node.row,node.column))
            return ErrorType()
        if method.is_error():
            return ErrorType()
        if len(method.param_types) != len(node.method_args):
            error = HulkSemanticError.INVALID_LEN_ARGUMENTS%(method.method_name,len(method.param_types),len(node.method_args))
            self.errors.append(HulkSemanticError(error,node.row,node.column))
            # return ErrorType()
        else:
            for index, (param_type, arg) in enumerate(zip(method.param_types,node.method_args)):
                arg_type = self.visit(arg,node.scope)
                try:
                    self.assign_type(param_type,arg_type)
                    # if param_type.is_error():
                    #     return ErrorType()
                except SemanticError:
                    error = HulkSemanticError.INVALID_TYPE_ARGUMENTS%(method.param_names[index], method.param_types[index].name,arg_type.name)
                    self.errors.append(HulkSemanticError(error,node.row,node.column))
                    # return ErrorType()
        return method.inferred_return_type

    @visitor.when(CallTypeAttributeNode)
    def visit(self, node:CallTypeAttributeNode, scope: Scope):
        node.scope = scope
        owner = self.visit(node.inst_name, node.scope)
        if owner.is_error():
            return ErrorType()
        if owner != self.current_type:
            error = HulkSemanticError.PRIVATE_ATTRIBUTE%(node.attribute, owner.name)
            self.errors.append(HulkSemanticError(error,node.row,node.column))
            return ErrorType()
        try:
            attribute = owner.get_attribute(node.attribute)
        except SemanticError as error:
            self.errors.append(HulkSemanticError(error,node.row,node.column))
            return ErrorType()
        else:
            return attribute.type
        
    
    
    @visitor.when(CastTypeNode)
    def visit(self, node:CastTypeNode, scope: Scope):
        node.scope = scope
        inst_type = self.visit(node.inst_name, node.scope)
        if inst_type.is_error():
            return ErrorType()
        
        if isinstance(inst_type,Type):
            try:
                type_cast = self.context.get_type(node.type_cast)
            except SemanticError as error:
                self.errors.append(HulkSemanticError(error,node.row,node.column))
                return ErrorType()
            else:
                if not type_cast.conforms_to(inst_type):
                    error = HulkSemanticError.INVALID_CAST_OPERATION%(inst_type.name,type_cast.name)
                    self.errors.append(HulkSemanticError(error,node.row,node.column))
        else:
            try:
                type_cast = self.context.get_type_or_protocol(node.type_cast)
            except SemanticError as error:
                self.errors.append(SemanticError(error))
                return ErrorType()
            else:
                if not type_cast.conforms_to(inst_type):
                    error = HulkSemanticError.INVALID_CAST_OPERATION%(inst_type.name,type_cast.name)
                    self.errors.append(HulkSemanticError(error,node.row,node.column))
        #No sé si retornar error o type_cast
        return type_cast

#_________________________________________________________________________________________________________________________
#_________________________________________________Unary__________________________________________________________________
    
    @visitor.when(ArithmeticUnaryNode)
    def visit(self, node: ArithmeticUnaryNode, scope: Scope):
        node.scope = scope
        operand_type = self.visit(node.operand, node.scope)

        if NumberType() == operand_type or operand_type.is_auto():
            return NumberType()
        elif not operand_type.is_error():
            error = HulkSemanticError.INVALID_UNARY_OPERATION%(operand_type.name)
            self.errors.append(HulkSemanticError(error,node.row,node.column))
        return NumberType()

    
    @visitor.when(BooleanUnaryNode)
    def visit(self, node: BooleanUnaryNode, scope: Scope):
        node.scope = scope
        operand_type = self.visit(node.operand, node.scope)

        if BooleanType() == operand_type or operand_type.is_auto():
            return BooleanType()
        elif not operand_type.is_error():
            error = HulkSemanticError.INVALID_UNARY_OPERATION%(operand_type.name)
            self.errors.append(HulkSemanticError(error,node.row,node.column))
        return BooleanType()
    

#_________________________________________________________________________________________________________________________
#__________________________________________________Literals__________________________________________________________________

    @visitor.when(BooleanNode)
    def visit(self, node: BooleanNode, scope: Scope):
        node.scope = scope
        return BooleanType()

    @visitor.when(StringNode)
    def visit(self, node: StringNode, scope: Scope):
        node.scope = scope
        return StringType()

    @visitor.when(NumberNode)
    def visit(self, node: NumberNode, scope: Scope):
        node.scope = scope
        return NumberType()
    

    @visitor.when(VarNode)
    def visit(self, node: VarNode, scope: Scope):
        node.scope = scope
        var = node.scope.find_variable(node.lex)
        if var is None:
            if node.lex == 'self':
                if(self.current_type is not None and self.current_method is not None):
                    return self.current_type
                else:
                    error = '"self" is not defined in this context'
                    self.errors.append(HulkSemanticError(error,node.row,node.column))
                    return ErrorType()
            else:
                error = HulkSemanticError.NOT_DEFINED%(node.lex)
                self.errors.append(HulkSemanticError(error,node.row,node.column))
                return ErrorType()
        else:
            return var.type 


        
    


         


