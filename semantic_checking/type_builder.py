import cmp.nbpackage
import cmp.visitor as visitor
from grammar.hulk_grammar import G
from grammar.ast_nodes import *
from cmp.semantic import *
from cmp.errors import HulkSemanticError


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
                self.errors.append(HulkSemanticError(error,node.row,node.column))

    @visitor.when(TypeDeclarationNode)
    def visit(self, node: TypeDeclarationNode): 
        if node.name in self.context.hulk_types:
            return
        current_type = self.context.get_type(node.name)
        if ErrorType() == current_type:
            return
        self.current_type = current_type
        param_types = []
        param_names = []
        names_count = {}
        
        for param in node.params:
            if(param[0]) in names_count:
                error = f'Type {node.name} has more than one parameter named {param[0]}'
                self.errors.append(HulkSemanticError(error,node.row,node.column))
                self.context.set_type_error(node.name)
                return
            else: 
                names_count[param] = 1
            try:
                param_type = self.context.get_type_or_protocol(param[1]) if param[1] is not None else AutoType()
            except SemanticError as error:
                error = HulkSemanticError.NOT_DEFINED_TYPE_CONSTRUCTOR_PARAM_TYPE%(param[1],param[0],self.current_type.name)
                self.errors.append(HulkSemanticError(error,node.row,node.column))
                param_type = ErrorType()
            param_names.append(param[0])
            param_types.append(param_type)
        self.current_type.set_params(param_names,param_types)

        for method in node.methods:
            try:
                self.visit(method) 
            except SemanticError as error:
                self.errors.append(HulkSemanticError(error,node.row,node.column))
        
        if node.parent in ['String','Boolean','Number']:
            error = HulkSemanticError.INVALID_INHERITANCE_FROM_DEFAULT_TYPE%(self.current_type.name,node.parent)
            self.errors.append(HulkSemanticError(error,node.row,node.column))
            parent = ErrorType()
        else:
            try:
                parent = self.context.get_type(node.parent)
            except SemanticError as error: 
                parent = ErrorType()
                error = HulkSemanticError.NOT_DEFINED_PARENT_TYPE%(node.parent,self.current_type.name)
                self.errors.append(HulkSemanticError(error,node.row,node.column))
            else:
                if parent.conforms_to(self.current_type):
                    parent = ErrorType()
                    error = HulkSemanticError.INVALID_CIRCULAR_INHERITANCE%(self.current_type.name,node.parent)
                    self.errors.append(HulkSemanticError(error,node.row,node.column))
        self.current_type.set_parent(parent)

        for attribute in node.attributes:
            try:
                self.visit(attribute) 
            except SemanticError as error:
                self.errors.append(HulkSemanticError(error,node.row,node.column))


    @visitor.when(ProtocolDeclarationNode)
    def visit(self, node: ProtocolDeclarationNode): 
        if node.name in self.context.hulk_protocols:
            return
        current_type = self.context.get_protocol(node.name)
        if ErrorType() == current_type:
            return
        self.current_type = current_type
      
        for method_sign in node.methods:
            try:
                self.visit(method_sign) 
            except SemanticError as error:
                self.errors.append(HulkSemanticError(error,node.row,node.column))

        if node.parent is None:
            parent = ObjectType()
        else:
            try:
                parent = self.context.get_protocol(node.parent)
            except SemanticError as error:
                error = HulkSemanticError.NOT_DEFINED_PARENT_TYPE%(node.parent,self.current_type)
                self.errors.append(HulkSemanticError(error,node.row,node.column))
                parent = ErrorType()
            else:
                if parent.conforms_to(self.current_type):
                    parent = ErrorType()
                    error = HulkSemanticError.INVALID_CIRCULAR_INHERITANCE%(self.current_type.name,node.parent)
                    self.errors.append(HulkSemanticError(error,node.row,node.column))
        self.current_type.set_parent(parent) 


    @visitor.when(FunctionDeclarationNode)
    def visit(self, node: FunctionDeclarationNode):   
        self.current_type = None
        try:
            return_type = self.context.get_type_or_protocol(node.returnType) if node.returnType is not None else AutoType()
        except SemanticError as error:
            error = HulkSemanticError.NOT_DEFINDED_FUNCTION_RETURN_TYPE%(node.returnType,node.name)
            self.errors.append(HulkSemanticError(error,node.row,node.column))
            return_type = ErrorType()

        param_types = []
        param_names = []
        names_count = {}
        for param in node.params:
            if(param[0]) in names_count:
                error = f'Function "{node.name}" has more than one parameter named "{param[0]}"'
                self.errors.append(HulkSemanticError(error,node.row,node.column))
                self.context.set_function_error(node.name)
                return
            else: 
                names_count[param] = 1
            try:
                param_type = self.context.get_type_or_protocol(param[1]) if param[1] is not None else AutoType()
            except SemanticError as error:
                error = HulkSemanticError.NOT_DEFINED_FUNCTION_PARAM_TYPE%(param[1],param[0],node.name)
                self.errors.append(HulkSemanticError(error,node.row,node.column))
                param_type = ErrorType()
            param_names.append(param[0])
            param_types.append(param_type)
        try:
            func = self.context.create_function(node.name,param_names,param_types,return_type)
            func.node = node

        except SemanticError as error: 
            self.errors.append(HulkSemanticError(error,node.row,node.column))
            if(node.name not in self.context.hulk_functions):
                self.context.set_function_error(node.name)


    @visitor.when(TypeAttributeNode)
    def visit(self, node: TypeAttributeNode): 
        try:
            type = self.context.get_type_or_protocol(node.type) if node.type is not None else AutoType()
        except:
            error = HulkSemanticError.NOT_DEFINED_ATTRIBUTE_TYPE%(node.type,node.name,self.current_type.name)
            self.errors.append(HulkSemanticError(error,node.row,node.column))
            type = ErrorType()
        try:
            attribute = self.current_type.define_attribute(node.name,type)
            attribute.node = node

        except SemanticError as error:
            self.errors.append(HulkSemanticError(error,node.row,node.column))
            self.current_type.set_attribute_error(node.name)
            # self.attributes.get_attribute(node.name).set_attribute_error()
            
            

    @visitor.when(MethodDeclarationNode)
    def visit(self, node: MethodDeclarationNode):   
        try:
            return_type = self.context.get_type_or_protocol(node.returnType) if node.returnType is not None else AutoType()
        except SemanticError as error:
            error = HulkSemanticError.NOT_DEFINED_METHOD_RETURN_TYPE%(node.returnType,node.name,self.current_type.name)
            self.errors.append(HulkSemanticError(error,node.row,node.column))
        param_types = []
        param_names = []
        names_count = {}
        for param in node.params:
            if param[0] in names_count:
                error = f'Method "{node.name}" in type "{self.current_type.name}" has more than one parameter named "{param[0]}"'
                self.errors.append(HulkSemanticError(error,node.row,node.column))
                self.current_type.set_method_error(node.name)
                return
            else: 
                names_count[param[0]] = 1
            try:
                param_type = self.context.get_type_or_protocol(param[1]) if param[1] is not None else AutoType()
            except SemanticError as error:
                error = HulkSemanticError.NOT_DEFINED_METHOD_PARAM_TYPE%(param[1],param[0],node.name,self.current_type.name)
                self.errors.append(HulkSemanticError(error,node.row,node.column))
                param_type = ErrorType()
            param_names.append(param[0])
            param_types.append(param_type)

        # param_types, param_names = zip(*[(self.context.get_type(param[1]), param[0]) for param in node.params])
        try:
            method = self.current_type.define_method(node.name,param_names,param_types,return_type)
            method.node = node
        except SemanticError as error:
            self.errors.append(HulkSemanticError(error,node.row,node.column))
            self.current_type.set_method_error(node.name)

    @visitor.when(MethodSignatureNode)
    def visit(self, node: MethodDeclarationNode): 
        if node.returnType is None:
            error = HulkSemanticError.NO_PROTOCOL_RETURN_TYPE%(node.name,self.current_type.name)
            self.errors.append(HulkSemanticError(error,node.row,node.column))
            return_type = ErrorType()
        else:
            try:
                return_type = self.context.get_type_or_protocol(node.returnType) 
            except SemanticError as error:
                error = HulkSemanticError.NOT_DEFINED_METHOD_RETURN_TYPE%(node.name,self.current_type.name)
                self.errors.append(HulkSemanticError(error,node.row,node.column))
                return_type = ErrorType()
        param_types = []
        param_names = []
        names_count = {}
        for param in node.params:
            if(param[0]) in names_count:
                error = f'Method "{node.name}" in protocol "{self.current_type.name}" has more than one parameter named "{param[0]}"'
                self.errors.append(HulkSemanticError(error,node.row,node.column))
                self.current_type.set_method_error(node.name)
                return
            else: 
                names_count[param] = 1
            if param[1] is None:
                error = HulkSemanticError.NO_PROTOCOL_PARAM_TYPE%(param[0],node.name,self.current_type.name)
                self.errors.append(HulkSemanticError(error,node.row,node.column))
                param_type = ErrorType()
            else:
                try:
                    param_type = self.context.get_type_or_protocol(param[1])
                except SemanticError as error:
                    error = HulkSemanticError.NOT_DEFINED_METHOD_PARAM_TYPE%(param[0],node.name,self.current_type.name)
                    self.errors.append(HulkSemanticError(error,node.row,node.column))
                    param_type = ErrorType()
            param_names.append(param[0])
            param_types.append(param_type)
        try:
            self.current_type.define_method(node.name,param_names,param_types,return_type)
        except SemanticError as error:
            self.errors.append(HulkSemanticError(error,node.row,node.column))
            self.current_type.set_method_error(node.name)
    