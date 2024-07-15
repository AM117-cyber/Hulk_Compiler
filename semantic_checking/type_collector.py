import cmp.visitor as visitor
from grammar.hulk_grammar import G
from grammar.ast_nodes import *
from cmp.semantic import *
from cmp.errors import HulkSemanticError

class TypeCollector(object):
    def __init__(self, errors=[]):
        self.context = None
        self.errors = errors
    
    @visitor.on('node')
    def visit(self, node):
        pass
    
    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode):
        self.context = Context()
        self.create_iterable_protocol()
        self.create_hulk_functions()
        for declaration in node.declarations:
            try:
                self.visit(declaration)
            except SemanticError as error:
                self.errors.append(HulkSemanticError(error,node.row,node.column))

    @visitor.when(TypeDeclarationNode)
    def visit(self, node :TypeDeclarationNode):
        try:
            new_type = self.context.create_type(node.name)
            new_type.node = node
        except SemanticError as error:
            self.errors.append(HulkSemanticError(error,node.row,node.column))
            if(node.name not in self.context.hulk_types):
                self.context.set_type_error(node.name)
    
    @visitor.when(ProtocolDeclarationNode)
    def visit(self, node :ProtocolDeclarationNode):
        try:
            new_protocol = self.context.create_protocol(node.name)
        except SemanticError as error:
            self.errors.append(HulkSemanticError(error,node.row,node.column))
            if(node.name not in self.context.hulk_protocols):
                self.context.set_protocol_error(node.name) 

    def create_hulk_functions(self):
        range_type:Type = self.context.create_type('Range')
        range_type.set_params(['min','max'],[NumberType(),NumberType()])
        range_type.define_attribute('min', NumberType())
        range_type.define_attribute('max', NumberType())
        range_type.define_attribute('current', NumberType())
        range_type.define_method('next',[],[],BooleanType())
        range_type.define_method('current',[],[],NumberType())
    
        self.context.create_function('sqrt', ['value'],[NumberType()],NumberType())
        self.context.create_function('sin', ['angle'],[NumberType()],NumberType())
        self.context.create_function('cos', ['angle'],[NumberType()],NumberType())
        self.context.create_function('exp',['value'],[NumberType()],NumberType())
        self.context.create_function('log',['base','value'],[NumberType(),NumberType()],NumberType())
        self.context.create_function('rand',[],[],NumberType())
        print_function = self.context.create_function('print',['obj'],[ObjectType()],ObjectType())
        self.context.create_function('range',['begin','end'],[NumberType(),NumberType()],range_type)

    def create_iterable_protocol(self):
        iterable_protocol: Protocol = self.context.create_protocol('Iterable')
        iterable_protocol.define_method('next',[],[],BooleanType())
        iterable_protocol.define_method('current',[],[],ObjectType())

