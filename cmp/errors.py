from colorama import Fore, Style

class HulkError(Exception):
    def __init__(self, text):
        super().__init__(text)

    @property
    def error_type(self):
        return 'HulkError'

    @property
    def text(self):
        return self.args[0]

    def __str__(self):
        return f'{self.error_type}: {self.text}'

    def __repr__(self):
        return str(self)
    
class HulkIOError(HulkError):
    INVALID_EXTENSION = 'Input file \'%s\' is not a .hulk file.'
    ERROR_READING_FILE = 'Error reading file \'%s\'.'
    ERROR_WRITING_FILE = 'Error writing to file \'%s\'.'

    @property
    def error_type(self):
        return 'IOHulkError'

class HulkSyntacticError(HulkError):
    def __init__(self, text, line, column):
        super().__init__(text)
        self.line = line
        self.column = column

    def __str__(self):
        return f'({self.line}, {self.column}) - {self.error_type}: {self.text}'

    Message = 'Error at or near \'%s\'.'

    @property
    def error_type(self):
        return 'SyntacticError'
    
class HulkLexicographicError(HulkError):
    def __init__(self, text, line, column):
        super().__init__(text)
        self.line = line
        self.column = column

    def __str__(self):
        return f"{Fore.RED}{self.error_type}: {self.text} -> (line: {self.line}, column: {self.column}){Style.RESET_ALL}"

    UNKNOWN_TOKEN = 'Unknown token \'%s\'.'
    UNTERMINATED_STRING = 'Unterminated string \'%s\'.'

    @property
    def error_type(self):
        return 'LEXICOGRAPHIC ERROR'
    
class HulkSemanticError(HulkError):
    def __init__(self, text, line, column):
        super().__init__(text)
        self.line = line
        self.column = column

    def __str__(self):
        return f"{Fore.RED}{self.error_type}: {self.text} -> (line: {self.line}, column: {self.column}){Style.RESET_ALL}"

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

    NOT_DEFINED_PROTOCOL_METHOD_RETURN_TYPE = 'Type or Protocol "%s" is not defined.'
    NO_PROTOCOL_RETURN_TYPE = 'A return type must me annoted for "%s" in Protocol "%s"'
    NO_PROTOCOL_PARAM_TYPE = 'A type must be annoted for parameter "%s" in method "%s" in Protocol "%s".'
    NOT_DEFINED_ATTRIBUTE_TYPE = 'Type "%s" of attribute "%s" in "%s" is not defined.'
    NOT_DEFINED_METHOD_RETURN_TYPE = 'Return type "%s" of method "%s" in "%s" is not defined.'
    NOT_DEFINDED_FUNCTION_RETURN_TYPE = 'Return type "%s" of function "%s" is not defined.'
    NOT_DEFINED_METHOD_PARAM_TYPE = 'Type "%s" of parameter"%s" in method "%s" in "%s" is not defined.'
    NOT_DEFINED_FUNCTION_PARAM_TYPE = 'Type "%s" of parameter"%s" in function "%s" is not defined.'
    NOT_DEFINED_TYPE_CONSTRUCTOR_PARAM_TYPE = 'Type "%s" of param "%s" in type "%s" declaration is not defined.'
    INVALID_INHERITANCE_FROM_DEFAULT_TYPE = 'Type "%s" can not inherite from Hulk Type "%s".'
    INVALID_CIRCULAR_INHERITANCE = '"%s" can not inherite from type "%s". Circular inheritance is not allowed.'
    NOT_DEFINED_PARENT_TYPE = 'Type %s of %s \'s parent is not defined '


    @property
    def error_type(self):
        return 'SEMANTIC ERROR'
    
class HulkRunTimeError(HulkError):
    def __init__(self, text, line, column):
        super().__init__(text)
        self.line = line
        self.column = column

    def __str__(self):
        return f"{Fore.RED}{self.error_type}: {self.text} -> (line: {self.line}, column: {self.column}){Style.RESET_ALL}"

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

    NOT_DEFINED_PROTOCOL_METHOD_RETURN_TYPE = 'Type or Protocol "%s" is not defined.'
    NO_PROTOCOL_RETURN_TYPE = 'A return type must me annoted for "%s" in Protocol "%s"'
    NO_PROTOCOL_PARAM_TYPE = 'A type must be annoted for parameter "%s" in method "%s" in Protocol "%s".'
    NOT_DEFINED_ATTRIBUTE_TYPE = 'Type "%s" of attribute "%s" in "%s" is not defined.'
    NOT_DEFINED_METHOD_RETURN_TYPE = 'Return type "%s" of method "%s" in "%s" is not defined.'
    NOT_DEFINDED_FUNCTION_RETURN_TYPE = 'Return type "%s" of function "%s" is not defined.'
    NOT_DEFINED_METHOD_PARAM_TYPE = 'Type "%s" of parameter"%s" in method "%s" in "%s" is not defined.'
    NOT_DEFINED_FUNCTION_PARAM_TYPE = 'Type "%s" of parameter"%s" in function "%s" is not defined.'
    NOT_DEFINED_TYPE_CONSTRUCTOR_PARAM_TYPE = 'Type "%s" of param "%s" in type "%s" declaration is not defined.'
    INVALID_INHERITANCE_FROM_DEFAULT_TYPE = 'Type "%s" can not inherite from Hulk Type "%s".'
    INVALID_CIRCULAR_INHERITANCE = '"%s" can not inherite from type "%s". Circular inheritance is not allowed.'
    NOT_DEFINED_PARENT_TYPE = 'Type %s of %s \'s parent is not defined '

    @property
    def error_type(self):
        return 'RUN TIME ERROR'
