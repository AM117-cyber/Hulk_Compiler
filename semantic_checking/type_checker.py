import cmp.nbpackage
import cmp.visitor as visitor
from grammar.hulk_grammar import G
from grammar.ast_nodes import *
from cmp.semantic import *

# changed
INCOMPATIBLE_TYPES = 'Cannot convert "%s" into "%s".'
WRONG_METHOD_RETURN_TYPE = 'Method "%s" in type "%s" return type is "%s" but it returns "%s"'
WRONG_FUNCTION_RETURN_TYPE = 'Function "%s" return type is "%s" but it returns "%s"'
WRONG_SIGNATURE = 'Method "%s" already defined in "%s" with a different signature.'
SELF_IS_READONLY = 'Variable "self" is read-only.'
LOCAL_ALREADY_DEFINED = 'Variable "%s" is already defined in method "%s".'
VARIABLE_NOT_DEFINED = 'Variable "%s" is not defined in "%s".'
INVALID_OPERATION = 'Operation is not defined between "%s" and "%s".'
INVALID_UNARY_OPERATION = 'Operation is not defined for "%s"'
VECTOR_OBJECT_DIFFERENT_TYPES = 'Types "%s" and "%s" are different in a vector'
INVALID_INDEXING = 'Cannot indexing in the "%s" variable'
INVALID_POSITION_INDEXING = 'Vector index cannot be a "%s"'
NOT_DEFINED = 'Variable "%s" is not defined'

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

#_____________________________________________________________________________________________________
#__________________________________________Declarations__________________________________________________________________
    
    @visitor.when(TypeDeclarationNode)
    def visit(self, node: TypeDeclarationNode, scope: Scope):
        self.current_type = self.context.get_type(node.name)
        if self.current_type.is_error():
            return
        
        for name, type in zip(self.current_type.param_names, self.current_type.param_types):
            scope.define_variable(name, type, True)
        child = scope.create_child()

        for attribute in node.attributes:
            try:
                self.visit(attribute, child) 
            except SemanticError as error:
                self.errors.append(error)
        for method in node.methods:
            try:
                self.visit(method, child.create_child()) 
            except SemanticError as error:
                self.errors.append(error)
        

    @visitor.when(TypeAttributeNode)
    def visit(self, node: TypeAttributeNode, scope: Scope):
        attribute: Attribute = self.current_type.get_attribute(node.name)

        expr_type = self.visit(node.value)
        var_type = attribute.type
        try:
            self.assign_type(var_type,expr_type)
        except SemanticError: 
            self.errors.append(SemanticError(INCOMPATIBLE_TYPES%(expr_type.name,attribute.type.name)))
        scope.define_variable(node.name,var_type)
        return var_type

    @visitor.when(MethodDeclarationNode)
    def visit(self, node: MethodDeclarationNode, scope: Scope):
        self.current_method = self.current_type.get_method(node.name)
        if self.current_method.is_error():
            return
        
        for name, type in zip(self.current_method.param_names, self.current_method.param_types):
            scope.define_variable(name, type, True)

        return_type = self.current_method.return_type
        for expr in node.body:
            expr_type = self.visit(expr,scope)
        
        try:
            self.assign_type(return_type,expr_type)
        except:
            self.errors.append(WRONG_METHOD_RETURN_TYPE%(self.current_method.name,self.current_type.name,self.current_method.return_type.name,expr_type.name))


    @visitor.when(FunctionDeclarationNode)
    def visit(self, node: FunctionDeclarationNode, scope: Scope):
        self.current_type = None
        self.current_method = self.context.get_function(node.name)
        if self.current_method.is_error():
            return
        
        for name, type in zip(self.current_method.param_names, self.current_method.param_types):
            scope.define_variable(name, type, True)

        return_type = self.current_method.return_type
        for expr in node.body:
            expr_type = self.visit(expr,scope)

        try:
            self.assign_type(return_type,expr_type)
        except:
            self.errors.append(WRONG_FUNCTION_RETURN_TYPE%(self.current_method.name,self.current_method.return_type.name,expr_type.name))




    def assign_type(self,var_type, expr_type):
        if var_type.is_error():
            return
        if expr_type.is_error():
            var_type = ErrorType()
        elif var_type.is_auto():
            var_type = expr_type
        elif not expr_type.conforms_to(var_type):
            var_type = ErrorType()
            raise SemanticError('Error')
            
#_____________________________________________________________________________________________________________________________________
#__________________________________________Expressions______________________________________________________________________________________

    # changed
    @visitor.when(WhileNode)
    def visit(self, node: WhileNode, scope: Scope):
        condition_type = self.visit(node.condition, scope)
        if BooleanType() != condition_type or not condition_type.is_auto():
            if not condition_type.is_error(): 
                self.errors.append(SemanticError(INCOMPATIBLE_TYPES%(condition_type.name, 'Boolean')))
            return ErrorType()
        
        body_type = self.visit(node.body, scope)
        return body_type
    
    # changed
    @visitor.when(ForNode)
    def visit(self, node: ForNode, scope: Scope):
        child_scope = scope.create_child()
        items_type = [self.visit(item, child_scope) for item in node.iterable]
        iterable_type = None
        count_auto = 0
        for item in items_type:
            if item.is_auto():
                count_auto += 1
            elif iterable_type is None and item != iterable_type:
                iterable_type = item
            elif iterable_type is not None and item != iterable_type:
                self.errors.append(SemanticError(VECTOR_OBJECT_DIFFERENT_TYPES%(iterable_type.name, item.name)))
                return ErrorType()
        if count_auto == len(items_type):
            iterable_type = AutoType()
        
        child_scope.define_variable(node.item.lex, iterable_type)

        body_type = self.visit(node.body, child_scope)
        return body_type
    
    # changed
    @visitor.when(ArithmeticBinaryNode)
    def visit(self, node: ArithmeticBinaryNode, scope: Scope):
        left_type = self.visit(node.left, scope)
        right_type = self.visit(node.right, scope)

        if (NumberType() == left_type or left_type.is_auto()) and (NumberType() == right_type or right_type.is_auto()):
            return NumberType()
        elif left_type.is_error() or right_type.is_error():
            return ErrorType()
        
        self.errors.append(SemanticError(INVALID_OPERATION%(left_type.name, right_type.name)))
        return ErrorType()
        
    # changed
    @visitor.when(DestrNode)
    def visit(self, node: DestrNode, scope: Scope):
        var_type = self.visit(node.var, scope)
        expr_type = self.visit(node.expr, scope)

        try:
            self.assign_type(var_type,expr_type)
        except:
            return ErrorType()
        else:
            return var_type

    # changed
    @visitor.when(ArithmeticUnaryNode)
    def visit(self, node: ArithmeticUnaryNode, scope: Scope):
        operand_type = self.visit(node.operand, scope)

        if NumberType() == operand_type or operand_type.is_auto():
            return NumberType()
        elif not operand_type.is_error():
            self.errors.append(SemanticError(INVALID_UNARY_OPERATION%(operand_type.name)))

        return ErrorType()
    
    # changed
    @visitor.when(BooleanUnaryNode)
    def visit(self, node: BooleanUnaryNode, scope: Scope):
        operand_type = self.visit(node.operand, scope)

        if BooleanType() == operand_type or operand_type.is_auto():
            return BooleanType()
        elif not operand_type.is_error():
            self.errors.append(SemanticError(INVALID_UNARY_OPERATION%(operand_type.name)))

        return ErrorType()

    # changed
    @visitor.when(BooleanBinaryNode)
    def visit(self, node: BooleanBinaryNode, scope: Scope):
        left_type = self.visit(node.left, scope)
        right_type = self.visit(node.right, scope)

        if (BooleanType() == left_type or left_type.is_auto()) and (BooleanType() == right_type or right_type.is_auto()):
            return BooleanType()
        elif left_type.is_error() or right_type.is_error():
            return ErrorType()
        
        self.errors.append(SemanticError(INVALID_OPERATION%(left_type.name, right_type.name)))
        return ErrorType()
    
    # changed
    @visitor.when(ExplicitVectorNode)
    def visit(self, node: ExplicitVectorNode, scope: Scope):
        items_type = [self.visit(item, scope) for item in node.items]
        iterable_type = None
        count_auto = 0
        for item in items_type:
            if item.is_auto():
                count_auto += 1
            elif iterable_type is None and item != iterable_type:
                iterable_type = item
            elif iterable_type is not None and item != iterable_type:
                self.errors.append(SemanticError(VECTOR_OBJECT_DIFFERENT_TYPES%(iterable_type.name, item.name)))
                return ErrorType()
        if count_auto == len(items_type):
            iterable_type = AutoType()
        
        return iterable_type
    
    # changed 
    @visitor.when(ImplicitVectorNode)
    def visit(self, node: ImplicitVectorNode, scope: Scope):
        child_scope = scope.create_child()
        items_type = [self.visit(item, child_scope) for item in node.iterable]
        iterable_type = None
        count_auto = 0
        for item in items_type:
            if item.is_error():
                return ErrorType()
            elif item.is_auto():
                count_auto += 1
            elif iterable_type is None and item != iterable_type:
                iterable_type = item
            elif iterable_type is not None and item != iterable_type:
                self.errors.append(SemanticError(VECTOR_OBJECT_DIFFERENT_TYPES%(iterable_type.name, item.name)))
                return ErrorType()
        if count_auto == len(items_type):
            iterable_type = AutoType()
        
        child_scope.define_variable(node.item.lex, iterable_type)

        expr_type = self.visit(node.expr, child_scope)
        return expr_type
    
    # changed
    @visitor.when(IndexObjectNode)
    def visit(self, node: IndexObjectNode, scope: Scope):
        pos_type = self.visit(node.pos, scope)
        if NumberType() != pos_type:
            self.errors.append(INVALID_POSITION_INDEXING%(pos_type.name))
            return ErrorType()
        
        object_type = self.visit(node.object, scope)
        if object_type.is_error():
            return ErrorType()
        elif StringType() != object_type or not isinstance(node.object, list):
            self.errors.append(INVALID_INDEXING%(node.object.lex))
            return ErrorType()
        
        return object_type
    
    # changed
    @visitor.when(BooleanNode)
    def visit(self, node: BooleanNode, scope: Scope):
        return BooleanType()
    
    # changed
    @visitor.when(StringNode)
    def visit(self, node: StringNode, scope: Scope):
        return StringType()
    
    # changed
    @visitor.when(NumberNode)
    def visit(self, node: NumberNode, scope: Scope):
        return NumberType()
    
    # changed
    @visitor.when(VarNode)
    def visit(self, node: VarNode, scope: Scope):
        var = scope.find_variable(node.lex)
        if var is None:
            self.errors.append(SemanticError(NOT_DEFINED%(node.lex)))
            return ErrorType()
        return var.type 

    # changed
    @visitor.when(TypeInstantiationNode)
    def visit(self, node: TypeInstantiationNode, scope: Scope):
        for argument in node.arguments:
            if ErrorType() == self.visit(argument, scope):
                return ErrorType()

        try:
            type_inst = self.context.get_type(node.name)
        except SemanticError as error:
            self.errors.append(SemanticError(error))
            return ErrorType

        return type_inst

        
    


         


