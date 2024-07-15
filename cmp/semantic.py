import itertools as itt
from collections import OrderedDict
from typing import Union



class SemanticError(Exception):
    @property
    def text(self):
        return self.args[0]

class Attribute:
    def __init__(self, name, typex = None):
        self.name = name
        self.type = typex
        self.value = None
        self.node = None

    def __str__(self):
        return f'[attrib] {self.name} : {self.type.name};'

    def __repr__(self):
        return str(self)
    
    def is_error(self):
        AttributeError() == self

    def set_type(self,typex):
        self.type = typex
    
    def set_value(self, value):
        self.value = value
    
class AttributeError(Attribute):
    def __init__(self):
        super().__init__('<error>',ErrorType())
    
    def __eq__(self,other):
        return isinstance(other, AttributeError) or other.name == self.name

class Method:
    def __init__(self, name, param_names, params_types, return_type):
        self.name = name
        self.param_names = param_names
        self.param_types = params_types
        self.return_type = return_type
        self.inferred_return_type = return_type
        self.node = None
        # self.inferred_param_types = params_types

    #changed
    def set_inferred_return_type(self,typex):
        self.inferred_return_type = typex
    
    # def set_inferred_param_type(self,param_name, param_type):
    #     self.inferred_param_types[param_name] = param_type

    def implements_method(self,other):
        if self.return_type.conforms_to(other.return_type) and all(param_other.conforms_to(param_self) for param_self, \
                                                                   param_other in zip(self.param_types, other.param_types)):
            return True
        return False

    def __str__(self):
        params = ', '.join(f'{n}:{t.name}' for n,t in zip(self.param_names, self.param_types))
        return f'[method] {self.name}({params}): {self.return_type.name} : {self.inferred_return_type.name};'

    def __eq__(self, other):
        return other.name == self.name and \
            other.return_type == self.return_type and \
            other.param_types == self.param_types
    
    def is_error(self):
        MethodError() == self

class MethodError(Method):
    def __init__(self):
        super().__init__('<error>', [], [], ErrorType())

    def __eq__(self, other):
        return isinstance(other, MethodError) or other.name == self.name
    
class Protocol:
    def __init__(self, name:str):
        self.name = name
        self.parent = None
        self.methods = {}

    def set_parent(self, parent):
        if self.parent is not None:
            raise SemanticError(f'Parent is already set for {self.name}.')
        self.parent = parent

    def is_auto(self):
        return False
    
    def is_error(self):
        return False
        
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

        try:
            self.get_method(name)
        except SemanticError:
            pass
        else: 
            raise SemanticError(f'Method "{name}" already defined in {self.name}. Protocols can not override methods')

        method = Method(name, param_names, param_types, return_type)
        self.methods[name] = method
        return method
    
    def set_method_error(self,key):
        self.methods[key] = MethodError()

    def __eq__(self, other):
        return self.name == other.name 
    
    def conforms_to(self, other):
        return other.bypass() or self == other or self.parent is not None and self.parent.conforms_to(other)
        # if other.bypass():
        #     return True
        # elif self == other:
        #     return True
        # elif self.parent is not None and self.parent.conforms_to(other):
        #     return True
        # else:
        #     return False
    def bypass(self):
        return False

    def __str__(self):
        output = f'protocol {self.name}'
        parent = '' if self.parent is None else f' : {self.parent.name}'
        output += parent
        output += ' {'
        output += '\n\t' if self.methods else ''
        output += '\n\t'.join(str(self.methods[x]) for x in self.methods )
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
        self.node = None

    #changed
    def __eq__(self, other):
        return self.name == other.name

    def is_error(self):
        return ErrorType() == self
    
    def is_auto(self):
        return AutoType() == self

    def set_params (self,param_names, param_types):
        self.param_names = param_names
        self.param_types = param_types

    #changed
    def find_params(self):
        if ObjectType() == self:
            return [],[]
        elif len(self.param_types) > 0:
                return self.param_names,self.param_types
        return self.parent.find_params()
    
      
            
 
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
        #Ver si es un error
        try:
            self.get_attribute(name)
        except SemanticError:
            attribute = Attribute(name, typex)
            self.attributes[name] = attribute
            return attribute
        else:
            raise SemanticError(f'Attribute "{name}" is already defined in {self.name}.')

        # if name in self.attributes:
        #     raise SemanticError(f'Attribute "{name}" is already defined in {self.name}.')
        

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
        if return_type is None:
            print(f'Nombre de metodo {name}, nombre de los parametros {param_names}')
            raise SemanticError(f'Return type for method "{name}" cannot be None')
        method = Method(name, param_names, param_types, return_type)
        self.methods[name] = method
        return method
    
    def set_method_error(self,key):
        self.methods[key] = MethodError()
    
    def set_attribute_error(self,key):
        self.attributes[key] = AttributeError()

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
        if other.is_auto():
            return True
        if isinstance(other,Type):
            return other.bypass() or self == other or self.parent is not None and self.parent.conforms_to(other)
        else:
            try:
               return all(self.get_method(other_method.name).implements_method(other_method) for other_method in other.methods.values())
            except SemanticError:
               return False
    def bypass(self):
        return False

        
    def __str__(self):
        output = f'type {self.name}'
        parent = '' if self.parent is None else f' : {self.parent.name}'
        output += parent
        output += ' {'
        output += '\n\t' if self.attributes or self.methods else ''
        output += '\n\t'.join(str(self.attributes[x]) for x in self.attributes)
        output += '\n\t' if self.attributes else ''
        output += '\n\t'.join(str(self.methods[x]) for x in self.methods )
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

    def conforms_to(self, other):
        return True
    
    def __eq__(self, other):
        return isinstance(other, AutoType) or other.name == self.name



class StringType(Type):
    def __init__(self):
        super().__init__('String')
        self.set_parent(ObjectType())

    def bypass(self):
        return True

    def __eq__(self, other):
        return isinstance(other, StringType) or other.name == self.name
    
    # def _init_(self, other):
    #     if other.


class BooleanType(Type):
    def __init__(self):
        super().__init__('Boolean')
        self.set_parent(ObjectType())
    def __eq__(self, other):
        return isinstance(other, BooleanType) or other.name == self.name


class NumberType(Type):
    def __init__(self) -> None:
        super().__init__('Number')
        self.set_parent(ObjectType())

    def __eq__(self, other):
        return isinstance(other, NumberType) or other.name == self.name

class ObjectType(Type):
    def __init__(self) -> None:
        super().__init__('Object')

    def __eq__(self, other):
        return isinstance(other, ObjectType) or other.name == self.name


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

class VectorType(Type):
    def __init__(self, element_type) -> None:
        super().__init__(f'{element_type.name}[]')
        self.set_parent(ObjectType())
        self.define_method('size', [], [], NumberType())
        self.define_method('next', [], [], BooleanType())
        self.define_method('current', [], [], element_type)

    def get_element_type(self) -> Union[Type, Protocol]:
        return self.get_method('current').return_type

    def conforms_to(self, other):
        if not isinstance(other, VectorType):
            return super().conforms_to(other)
        self_elem_type = self.get_element_type()
        other_elem_type = other.get_element_type()
        return self_elem_type.conforms_to(other_elem_type)

    def __eq__(self, other):
        return isinstance(other, VectorType) or other.name == self.name

def get_vector_type(items_type):
    iterable_type = None
    count_auto = 0
    for item in items_type:
        if item.is_auto():
            count_auto += 1
        elif iterable_type is None and item is not None and not item.is_error():
            iterable_type = item
        elif iterable_type is not None and item != iterable_type and not item.is_error():
            raise 'Error'
    if count_auto == len(items_type):
        iterable_type = AutoType()
    return iterable_type

    # def conforms_to(self, other):
    #     return True

    # def bypass(self):
    #     return True
# SemanticError(VECTOR_OBJECT_DIFFERENT_TYPES%(iterable_type.name, item.name)))

# class IntType(Type):
#     def __init__(self):
#         Type.__init__(self, 'int')

#     def __eq__(self, other):
#         return other.name == self.name or isinstance(other, IntType)

class Context:
    def __init__(self):
        self.types = {'String':StringType(), 'Boolean':BooleanType(),'Number':NumberType(), 'Object': ObjectType()}
        self.protocols = {}
        self.functions = {}
        self.hulk_types = {'String','Boolean','Number','Object', 'Range'}
        self.hulk_protocols = {'Iterable'}
        self.hulk_functions = {'sqrt','sin','cos','exp','log','rand','print','range'}

    def create_type(self, name:str):
        if name in self.types:
            raise SemanticError(f'Type with the same name "{name}" already in context.')
        if name in self.protocols:
            raise SemanticError(f'Protocol with the same name "{name}" already in context.')
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
            raise SemanticError(f'Protocol with the same name "{name}" already in context.')
        if name in self.types:
            raise SemanticError(f'Type with the same name "{name}" already in context.')
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
            return self.get_type(name)
        except SemanticError:
            try:
                return self.get_protocol(name)
            except SemanticError:
                raise SemanticError(f'Type or Protocol "{name}" is not defined')


    def create_function(self, name:str, param_names, param_types,return_type):
        if name in self.functions:
            raise SemanticError(f'Function with the same name "{name}" already in context.')
        functionx = self.functions[name] = Method(name, param_names, param_types, return_type)
        return functionx 
    
    def get_function(self, name:str):
        try:
            return self.functions[name]
        except KeyError:
            raise SemanticError(f'Function "{name}" is not defined.')
    
    def set_function_error(self,key):
        self.functions[key] = MethodError()

    
    def __str__(self):
        return ('{\n\t' +
                '\n\t'.join(y for x in self.types.values() for y in str(x).split('\n')) +
                '\n\t'.join(y for x in self.protocols.values() if not isinstance(x,ErrorType) for y in str(x).split('\n')) +
                '\n\t'.join(y for x in self.functions.values() for y in str(x).split('\n')) +
                '\n}')



    def __repr__(self):
        return str(self)

class VariableInfo:
    def __init__(self, name, vtype, is_error = False, is_parameter = False):
        self.name = name
        self.type = vtype
        self.is_parameter = is_parameter
        self.is_error = is_error
        self.value = None
    
    def set_type(self, vtype):
        self.type = vtype
    
    def set_value(self, value):
        self.value = value

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

    def define_variable(self, vname, vtype, is_parameter = False):
        info = VariableInfo(vname, vtype, is_parameter)
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

#changed
def get_lowest_common_ancestor(types):
   
    if not types or any(isinstance(t, ErrorType) for t in types):
        return ErrorType()
    if any(t == AutoType() for t in types):
        return AutoType()
    lca = types[0]
    for typex in types[1:]:
        lca = _get_lca(lca, typex)
    return lca


def _get_lca(type1: Type, type2: Type):
    # Object is the "root" of protocols too
    if type1 is None or type2 is None:
        return ObjectType()
    if type1.conforms_to(type2):
        return type2
    if type2.conforms_to(type1):
        return type1
    return _get_lca(type1.parent, type2.parent)

def _get_lca(first_type: Type, second_type: Type):
    # Object is the "root" of protocols too
    if first_type is None or second_type is None:
        return ObjectType()
    if first_type.conforms_to(second_type):
        return second_type
    if second_type.conforms_to(first_type):
        return first_type
    return _get_lca(first_type.parent, second_type.parent)