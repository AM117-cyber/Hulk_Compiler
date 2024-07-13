
import sys
import dill
from cmp.errors import HulkSyntacticError
from cmp.utils import Token
from grammar.hulk_grammar import *
from lexer.hulk_token_types import TokenType
from parser.parsing import ParserError, SLR1Parser

class HulkParser(SLR1Parser):
    def __init__(self):
        super().__init__(G, verbose=True)

    def __call__(self, tokens):
        try:
            mapped_terminals = [tokens_terminals_map[t.token_type] for t in tokens]
            derivation, operations = super().__call__(mapped_terminals)
            return derivation, operations, []
        except ParserError as error:
            error_token = tokens[error.token_index]
            error_text = HulkSyntacticError.Message % error_token.lex
            errors = [HulkSyntacticError(error_text, error_token.row, error_token.col)]
            return None, None, errors

tokens_terminals_map = {
    G.EOF: G.EOF,
    TokenType.OPEN_PAREN: o_par,
    TokenType.CLOSE_PAREN: c_par,
    TokenType.OPEN_CURLY: o_curly,
    TokenType.CLOSE_CURLY: c_curly,
    TokenType.OPEN_SQUARE_BRACKET: o_square_bracket,
    TokenType.CLOSE_SQUARE_BRACKET: c_square_bracket,
    TokenType.COMMA: comma,
    TokenType.DOT: dot,
    TokenType.COLON: colon,
    TokenType.SEMICOLON: semicolon,
    TokenType.ARROW: arrow,
    TokenType.DOUBLE_BAR: such_that_op,
    TokenType.ASSIGNMENT: assign_op,
    TokenType.DEST_ASSIGNMENT: destr_op,

    TokenType.IDENTIFIER: id_,
    TokenType.STRING: string_,
    TokenType.NUMBER: num,
    TokenType.BOOLEAN: bool_,

    # Arithmetic operators
    TokenType.PLUS: plus_op,
    TokenType.MINUS: minus_op,
    TokenType.STAR: mult_op,
    TokenType.DIV: div_op,
    TokenType.MOD: mod_op,
    TokenType.POWER: pow_op,
    TokenType.DOUBLE_STAR: double_star_op,

    # Boolean operators
    TokenType.AND: and_op,
    TokenType.OR: or_op,
    TokenType.NOT: not_op,

    # Concat strings operators
    TokenType.AMP: concat_op,
    TokenType.DOUBLE_AMP: double_concat_op,

    # Comparison operators
    TokenType.EQ: equal,
    TokenType.NEQ: not_equal,
    TokenType.LEQ: leth,
    TokenType.GEQ: geth,
    TokenType.LT: lth,
    TokenType.GT: gth,

    # Keywords
    TokenType.FUNCTION: function_,
    TokenType.LET: let,
    TokenType.IN: in_,
    TokenType.IF: if_,
    TokenType.ELSE: else_,
    TokenType.ELIF: elif_,
    TokenType.WHILE: while_,
    TokenType.FOR: for_,
    TokenType.NEW: new,
    TokenType.IS: is_,
    TokenType.AS: as_,
    TokenType.PROTOCOL: protocol_,
    TokenType.EXTENDS: extends,
    TokenType.TYPE: type_,
    TokenType.INHERITS: inherits
}
                
