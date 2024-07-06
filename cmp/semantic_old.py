import itertools as itt
from collections import OrderedDict


class SemanticError(Exception):
    @property
    def text(self):
        return self.args[0]

class Attribute:
    def __init__(self, name, typex = None):
        self.name = name
        self.type = typex

    def __str__(self):
        return f'[attrib] {self.name} : {self.type.name};'

    def __repr__(self):
        return str(self)

class Method:
    def __init__(self, name, param_names, params_types, return_type):
        self.name = name
        self.param_names = param_names
        self.param_types = params_types
        self.return_type = return_type

    def __str__(self):
        params = ', '.join(f'{n}:{t.name}' for n,t in zip(self.param_names, self.param_types))
        return f'[method] {self.name}({params}): {self.return_type.name};'

    def __eq__(self, other):
        return other.name == self.name and \
            other.return_type == self.return_type and \
            other.param_types == self.param_types
    
class Protocol:
    def __init__(self, name:str):
        self.name = name
        self.parent = None
        self.methods = {}

    def set_parent(self, parent):
        if self.parent is not None:
            raise SemanticError(f'Parent protocol is already set for {self.name}.')
        self.parent = parent

    def get_method(self, name: str):
        if name in self.methods:
            return self.methods[name]
        if self.parent is None:
            raise SemanticError(f'Method "{name}" is not defined in {self.name}.')
        try:
            return self.parent.get_method(name)
        except SemanticError:
            raise SemanticError(f'Method "{name}" is not defined in {self.name}.')
 
    def define_method(self, name: str, param_names: list, param_types: list, return_type):
        if name in self.methods:
            raise SemanticError(f'Method "{name}" already defined in {self.name}')
        method = Method(name, param_names, param_types, return_type)
        self.methods[name] = method
        return method
    
    def set_method_error(self,key):
        self.methods[key] = ErrorType()
    
    def conforms_to(self, other):
        return other.bypass() or self == other or self.parent is not None and self.parent.conforms_to(other)

    def bypass(self):
        return False

    def __str__(self):
        output = f'type {self.name}'
        parent = '' if self.parent is None else f' : {self.parent.name}'
        output += parent
        output += ' {'
        output += '\n\t' if self.methods else ''
        output += '\n\t'.join(str(self.methods[x]) for x in self.methods if not isinstance(self.methods[x], ErrorType))
        output += '\n' if self.methods else ''
        output += '}\n'
        return output

    def __repr__(self):
        return str(self)

class Type:
    def __init__(self, name:str):
        self.name = name
        self.attributes = {}
        self.methods = {}
        self.parent = None
        self.param_names = []
        self.param_types = []

    def set_params (self,param_names, param_types):
        self.param_names = param_names
        self.param_types = param_types

    def set_parent(self, parent):
        if self.parent is not None:
            raise SemanticError(f'Parent type is already set for {self.name}.')
        self.parent = parent

    def get_attribute(self, name: str):
        try:
            return self.attributes[name]
        except KeyError:
            if self.parent is None:
                raise SemanticError(f'Attribute "{name}" is not defined in {self.name}.')
            try:
                return self.parent.get_attribute(name)
            except SemanticError:
                raise SemanticError(f'Attribute "{name}" is not defined in {self.name}.')

    def define_attribute(self, name: str, typex):
            if name in self.attributes:
                raise SemanticError(f'Attribute "{name}" is already defined in {self.name}.')
            attribute = Attribute(name, typex)
            self.attributes[name] = attribute
            return attribute

    def get_method(self, name: str):
        if name in self.methods:
            return self.methods[name]
        if self.parent is None:
            raise SemanticError(f'Method "{name}" is not defined in {self.name}.')
        try:
            return self.parent.get_method(name)
        except SemanticError:
            raise SemanticError(f'Method "{name}" is not defined in {self.name}.')
 
    def define_method(self, name: str, param_names: list, param_types: list, return_type):
        if name in self.methods:
            raise SemanticError(f'Method "{name}" already defined in {self.name}')
        method = Method(name, param_names, param_types, return_type)
        self.methods[name] = method
        return method
    
    def set_method_error(self,key):
        self.methods[key] = ErrorType()
    
    def set_attribute_error(self,key):
        self.attributes[key] = ErrorType()

    def all_attributes(self, clean=True):
        plain = OrderedDict() if self.parent is None else self.parent.all_attributes(False)
        for attr in self.attributes.values():
            plain[attr.name] = (attr, self)
        return list(plain.values()) if clean else plain

    def all_methods(self, clean=True):
        plain = OrderedDict() if self.parent is None else self.parent.all_methods(False)
        for name, method in self.methods.items():
            plain[name] = (method, self)
        return plain.values() if clean else plain

    def conforms_to(self, other):
        return other.bypass() or self == other or self.parent is not None and self.parent.conforms_to(other)

    def bypass(self):
        return False

        
    def __str__(self):
        output = f'type {self.name}'
        parent = '' if self.parent is None else f' : {self.parent.name}'
        output += parent
        output += ' {'
        output += '\n\t' if self.attributes or self.methods else ''
        output += '\n\t'.join(str(self.attributes[x]) for x in self.attributes if not isinstance(self.attributes[x], ErrorType))
        output += '\n\t' if self.attributes else ''
        output += '\n\t'.join(str(self.methods[x]) for x in self.methods if not isinstance(self.methods[x], ErrorType))
        output += '\n' if self.methods else ''
        output += '}\n'
        return output

    def __repr__(self):
        return str(self)

class ErrorType(Type):
    def __init__(self):
        super().__init__('<error>')

    def conforms_to(self, other):
        return True

    def bypass(self):
        return True

    def __eq__(self, other):
        return isinstance(other, ErrorType) or other.name == self.name


class AutoType(Type):
    def __init__(self):
        Type.__init__(self, '<auto>')
    
    def bypass(self):
        return True

    def __eq__(self, other):
        return isinstance(other, AutoType) or other.name == self.name



class StringType(Type):
    def __init__(self):
        super().__init__('String')
        self.set_parent(ObjectType())



class BooleanType(Type):
    def __init__(self):
        super().__init__('Boolean')
        self.set_parent(ObjectType())



class NumberType(Type):
    def __init__(self) -> None:
        super().__init__('Number')
        self.set_parent(ObjectType())



class ObjectType(Type):
    def __init__(self) -> None:
        super().__init__('Object')



class SelfType(Type):
    def __init__(self, referred_type: Type = None) -> None:
        super().__init__('Self')
        self.referred_type = referred_type

    def get_attribute(self, name: str) -> Attribute:
        if self.referred_type:
            return self.referred_type.get_attribute(name)

        return super().get_attribute(name)

    def __eq__(self, other):
        return isinstance(other, SelfType) or other.name == self.name


    # def conforms_to(self, other):
    #     return True

    # def bypass(self):
    #     return True


# class IntType(Type):
#     def __init__(self):
#         Type.__init__(self, 'int')

#     def __eq__(self, other):
#         return other.name == self.name or isinstance(other, IntType)

class Context:
    def __init__(self):
        self.types = {'String':StringType, 'Boolean':BooleanType(),'Number':NumberType(), 'Object': ObjectType}
        self.protocols = {}
        self.functions = {}

    def create_type(self, name:str):
        if name in self.types:
            raise SemanticError(f'Type with the same name ({name}) already in context.')
        if name in self.protocols:
            raise SemanticError(f'Protocol with the same name ({name}) already in context.')
        typex = self.types[name] = Type(name)
        return typex

    def get_type(self, name:str):
        try:
            return self.types[name]
        except KeyError:
            raise SemanticError(f'Type "{name}" is not defined.')
    
    def set_type_error(self,key):
        self.types[key] = ErrorType()
        

    def create_protocol(self, name:str):
        if name in self.protocols:
            raise SemanticError(f'Protocol with the same name ({name}) already in context.')
        if name in self.types:
            raise SemanticError(f'Type with the same name ({name}) already in context.')
        protocolx = self.protocols[name] = Protocol(name)
        return protocolx  
    
    def get_protocol(self, name:str):
        try:
            return self.protocols[name]
        except KeyError:
            raise SemanticError(f'Protocol "{name}" is not defined.')

    def set_protocol_error(self,key):
        self.protocols[key] = ErrorType()

    def get_type_or_protocol(self, name:str):
        try:
            self.get_type(name)
        except KeyError:
            try:
                self.get_protocol(name)
            except KeyError:
                raise SemanticError(f'Type or Protocol "{name}" is not defined')


    def create_function(self, name:str, param_names, param_types,return_type):
        if name in self.functions:
            raise SemanticError(f'Function with the same name ({name}) already in context.')
        functionx = self.functions[name] = [Method(name, param_names, param_types, return_type),False]
        return functionx 
    
    def get_function(self, name:str):
        try:
            return self.functions[name]
        except KeyError:
            raise SemanticError(f'Function "{name}" is not defined.')
    
    def set_function_error(self,key):
        self.functions[key] = ErrorType()

    # def reset_types(self):
    #     flag = False
    #     for type in self.types:
    #         if flag:
    #             self.types[type][1] = False
    #         if type == 'Object':
    #             flag = True

    # def reset_protocols(self):
    #     self.reset(self.protocols,'Iterable')

    # def reset_functions(self):
    #     self.reset(self.functions,'')

    # def reset (self, dict, s_key):
    #     flag = False
    #     for item in self.items:
    #         if flag:
    #             dict[item][1] = False
    #         if item == s_key:
    #             flag = True    

    # def __str__(self):
    #     return '{\n\t' + '\n\t'.join(y for x in self.types.values() for y in str(x).split('\n')) + '\n}'
    
    def __str__(self):
        return ('{\n\t' +
                '\n\t'.join(y for x in self.types.values() if not isinstance(x,ErrorType) for y in str(x).split('\n')) +
                '\n\t'.join(y for x in self.protocols.values() if not isinstance(x,ErrorType) for y in str(x).split('\n')) +
                '\n\t'.join(y for x in self.functions.values() if not isinstance(x,ErrorType) for y in str(x).split('\n')) +
                '\n}')



    def __repr__(self):
        return str(self)

class VariableInfo:
    def __init__(self, name, vtype):
        self.name = name
        self.type = vtype

class Scope:
    def __init__(self, parent=None):
        self.locals = []
        self.parent = parent
        self.children = []
        self.index = 0 if parent is None else len(parent)

    def __len__(self):
        return len(self.locals)

    def create_child(self):
        child = Scope(self)
        self.children.append(child)
        return child

    def define_variable(self, vname, vtype):
        info = VariableInfo(vname, vtype)
        self.locals.append(info)
        return info

    def find_variable(self, vname, index=None):
        locals = self.locals if index is None else itt.islice(self.locals, index)
        try:
            return next(x for x in locals if x.name == vname)
        except StopIteration:
            return self.parent.find_variable(vname, self.index) if self.parent is not None else None

    def is_defined(self, vname):
        return self.find_variable(vname) is not None

    def is_local(self, vname):
        return any(True for x in self.locals if x.name == vname)
