from enum import Enum, auto

class TokenType(Enum):
    OPEN_PAREN = auto()
    CLOSE_PAREN = auto()
    OPEN_CURLY = auto()
    CLOSE_CURLY = auto()
    OPEN_SQUARE_BRACKET = auto()
    CLOSE_SQUARE_BRACKET = auto()
    COMMA = auto()
    DOT = auto()
    COLON = auto()
    SEMICOLON = auto()
    ARROW = auto()
    DOUBLE_BAR = auto()
    ASSIGNMENT = auto()
    DEST_ASSIGNMENT = auto()

    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()
    BOOLEAN = auto()
    PI = auto()
    EULER = auto()

    # Arithmetic operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    DIV = auto()
    MOD = auto()
    POWER = auto()
    DOUBLE_STAR = auto()

    # Boolean operators
    AND = auto()
    OR = auto()
    NOT = auto()

    # Concat strings operators
    AMP = auto()
    DOUBLE_AMP = auto()

    # Comparison operators
    EQ = auto()
    NEQ = auto()
    LEQ = auto()
    GEQ = auto()
    LT = auto()
    GT = auto()

    # Keywords
    FUNCTION = auto()
    LET = auto()
    IN = auto()
    IF = auto()
    ELSE = auto()
    ELIF = auto()
    WHILE = auto()
    FOR = auto()
    NEW = auto()
    IS = auto()
    AS = auto()
    PROTOCOL = auto()
    EXTENDS = auto()
    TYPE = auto()
    INHERITS = auto()

    # Tokens that don't have any syntactic meaning
    UNTERMINATED_STRING = auto()
    ESCAPED_CHAR = auto()
    SPACES = auto()
