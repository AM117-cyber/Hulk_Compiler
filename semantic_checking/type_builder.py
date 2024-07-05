import cmp.nbpackage
import cmp.visitor as visitor
from grammar.hulk_grammar import G
from grammar.ast_nodes import *
from cmp.semantic import *

WRONG_SIGNATURE = 'Method "%s" already defined in "%s" with a different signature.'
NOT_DEFINED_PROTOCOL_METHOD_RETURN_TYPE = 'Type or Protocol "%s" is not defined.'
NO_PROTOCOL_RETURN_TYPE = 'A return type must me annoted for "%s" in Protocol "%s"'
NO_PROTOCOL_PARAM_TYPE = 'A type must be annoted for parameter "%s" in method "%s" in Protocol "%s".'
NOT_DEFINED_ATTRIBUTE_TYPE = 'Type "%s" of attribute "%s" in "%s" is not defined.'
NOT_DEFINED_METHOD_RETURN_TYPE = 'Return type "%s" of method "%s" in "%s" is not defined.'
NOT_DEFINDED_FUNCTION_RETURN_TYPE = 'Return type "%s" of function "%s" is not defined.'
NOT_DEFINED_METHOD_PARAM_TYPE = 'Type "%s" of parameter "%s" in method "%s" in "%s" is not defined.'
NOT_DEFINED_FUNCTION_PARAM_TYPE = 'Type "%s" of parameter "%s" in function "%s" is not defined.'
NOT_DEFINED_TYPE_CONSTRUCTOR_PARAM_TYPE = 'Type "%s" of param "%s" in type "%s" declaration is not defined.'
INVALID_INHERITANCE_FROM_DEFAULT_TYPE = 'Type "%s" can not inherite from Hulk Type "%s".'
INVALID_CIRCULAR_INHERITANCE = '"%s" can not inherite from type "%s". Circular inheritance is not allowed.'
NOT_DEFINED_PARENT_TYPE = 'Type %s of %s \'s parent is not defined '


class TypeBuilder:
    def __init__(self, context, errors=[]):
        self.context = context
        self.current_type = None
        self.errors = errors
    
    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode):
        for declaration in node.declarations:
            try:
                self.visit(declaration)
            except SemanticError as error:
                self.errors.append(error)

    @visitor.when(TypeDeclarationNode)
    def visit(self, node: TypeDeclarationNode): 
        current_type = self.context.get_type(node.name)
        if current_type.is_error():
            return
        self.current_type = current_type
        param_types = []
        param_names = []
        names_count = {}
        
        for param in node.params:
            if(param[0]) in names_count:
                self.errors.append(SemanticError(f'Type {node.name} has more than one parameter named {param[0]}'))
                self.context.set_type_error(node.name)
                return
            else: 
                names_count[param] = 1
            try:
                param_type = self.context.get_type_or_protocol(param[1]) if param[1] is not None else AutoType()
            except SemanticError as error:
                self.errors.append(NOT_DEFINED_TYPE_CONSTRUCTOR_PARAM_TYPE%(param[1],param[0],self.current_type.name))
                param_type = ErrorType()
            param_names.append(param[0])
            param_types.append(param_type)
        self.current_type.set_params(param_names,param_types)

        if node.parent in ['String','Boolean','Number','Vector']:
            self.errors.append(INVALID_INHERITANCE_FROM_DEFAULT_TYPE%(self.current_type.name,node.parent))
            parent = ErrorType()
        else:
            try:
                parent = self.context.get_type(node.parent)
            except SemanticError as error: 
                parent = ErrorType()
                self.errors.append(NOT_DEFINED_PARENT_TYPE%(node.parent,self.current_type.name))
            else:
                if parent.conforms_to(self.current_type):
                    parent = ErrorType()
                    self.errors.append(INVALID_CIRCULAR_INHERITANCE%(self.current_type.name,node.parent))
        self.current_type.set_parent(parent)

        for method in node.methods:
            try:
                self.visit(method) 
            except SemanticError as error:
                self.errors.append(error)
        for attribute in node.attributes:
            try:
                self.visit(attribute) 
            except SemanticError as error:
                self.errors.append(error)


    @visitor.when(ProtocolDeclarationNode)
    def visit(self, node: ProtocolDeclarationNode): 
        current_type = self.context.get_protocol(node.name)
        if ErrorType() == current_type:
            return
        self.current_type = current_type
      
        if node.parent is None:
            parent = AutoType()
        else:
            try:
                parent = self.context.get_protocol(node.parent)
            except SemanticError as error:
                self.errors.append(NOT_DEFINED_PARENT_TYPE%(node.parent,self.current_type))
                parent = TypeError()
            else:
                if parent.conforms_to(self.current_type):
                    parent = TypeError()
                    self.errors.append(INVALID_CIRCULAR_INHERITANCE%(self.current_type.name,node.parent))
        self.current_type.set_parent(parent) 
        for method_sign in node.methods:
            try:
                self.visit(method_sign) 
            except SemanticError as error:
                self.errors.append(error)


    @visitor.when(FunctionDeclarationNode)
    def visit(self, node: FunctionDeclarationNode):   
        self.current_type = None
        try:
            return_type = self.context.get_type_or_protocol(node.returnType) if node.returnType is not None else AutoType()
        except SemanticError as error:
            self.errors.append(NOT_DEFINDED_FUNCTION_RETURN_TYPE%(node.returnType,node.name))
            return_type = ErrorType()

        param_types = []
        param_names = []
        names_count = {}
        for param in node.params:
            if(param[0]) in names_count:
                self.errors.append(SemanticError(f'Function {node.name} has more than one parameter named {param[0]}'))
                self.context.set_function_error(node.name)
                return
            else: 
                names_count[param] = 1
            try:
                param_type = self.context.get_type_or_protocol(param[1]) if param[1] is not None else AutoType()
            except SemanticError as error:
                self.errors.append(NOT_DEFINED_FUNCTION_PARAM_TYPE%(param[1],param[0],node.name))
                param_type = ErrorType()
            param_names.append(param[0])
            param_types.append(param_type)
        try:
            self.context.create_function(node.name,param_names,param_types,return_type)
        except SemanticError as error: 
            self.errors.append(error)
            self.context.set_function_error(node.name)


    @visitor.when(TypeAttributeNode)
    def visit(self, node: TypeAttributeNode): 
        try:
            type = self.context.get_type_or_protocol(node.type) if node.type is not None else AutoType()
        except:
            self.errors.append(NOT_DEFINED_ATTRIBUTE_TYPE%(node.type,node.name,self.current_type.name))
            type = ErrorType()
        try:
            self.current_type.define_attribute(node.name,type)
        except SemanticError as error:
            self.errors.append(error)
            self.current_type.set_attribute_error(node.name)

    @visitor.when(MethodDeclarationNode)
    def visit(self, node: MethodDeclarationNode):   
        try:
            return_type = self.context.get_type_or_protocol(node.returnType) if node.returnType is not None else AutoType()
        except SemanticError as error:
            self.errors.append(NOT_DEFINED_METHOD_RETURN_TYPE%(node.returnType,node.name,self.current_type.name))
            return_type = ErrorType()
        param_types = []
        param_names = []
        names_count = {}
        for param in node.params:
            if(param[0]) in names_count:
                self.errors.append(SemanticError(f'Method {node.name} in type {self.current_type.name} has more than one parameter named {param[0]}'))
                self.current_type.set_method_error(node.name)
                return
            else: 
                names_count[param] = 1
            try:
                param_type = self.context.get_type_or_protocol(param[1]) if param[1] is not None else AutoType()
            except SemanticError as error:
                self.errors.append(NOT_DEFINED_METHOD_PARAM_TYPE%(param[1],param[0],node.name,self.current_type.name))
                param_type = ErrorType()
            param_names.append(param[0])
            param_types.append(param_type)

        # param_types, param_names = zip(*[(self.context.get_type(param[1]), param[0]) for param in node.params])
        try:
            self.current_type.define_method(node.name,param_names,param_types,return_type)
        except SemanticError as error:
            self.errors.append(error)
            self.current_type.set_method_error(node.name)

    @visitor.when(MethodSignatureNode)
    def visit(self, node: MethodSignatureNode): 
        if node.returnType is None:
            self.errors.append(NO_PROTOCOL_RETURN_TYPE%(node.name,self.current_type.name))
            return_type = ErrorType()
        else:
            try:
                return_type = self.context.get_type_or_protocol(node.returnType) 
            except SemanticError as error:
                self.errors.append(NOT_DEFINED_METHOD_RETURN_TYPE%(node.name,self.current_type.name))
                return_type = ErrorType()
        param_types = []
        param_names = []
        names_count = {}
        for param in node.params:
            if(param[0]) in names_count:
                self.errors.append(SemanticError(f'Method {node.name} in protocol {self.current_type.name} has more than one parameter named {param[0]}'))
                self.current_type.set_method_error(node.name)
                return
            else: 
                names_count[param] = 1
            if param[1] is None:
                self.errors.append(NO_PROTOCOL_PARAM_TYPE%(param[0],node.name,self.current_type.name))
                param_type = ErrorType()
            else:
                try:
                    param_type = self.context.get_type_or_protocol(param[1])
                except SemanticError as error:
                    self.errors.append(NOT_DEFINED_METHOD_PARAM_TYPE%(param[1], param[0],node.name,self.current_type.name))
                    param_type = ErrorType()
            param_names.append(param[0])
            param_types.append(param_type)
        try:
            self.current_type.define_method(node.name,param_names,param_types,return_type)
        except SemanticError as error:
            self.errors.append(error)
            self.current_type.set_method_error(node.name)
    