import math
import dill
import sys
from cmp.utils import Token
from lexer.hulk_token_types import TokenType
from cmp.errors import HulkLexicographicError
from lexer.lexer_generator import Lexer
from lexer.regex_tokens import hulk_tokens
from grammar.hulk_grammar import G

class HulkLexer(Lexer):
    def __init__(self):
        super().__init__(hulk_tokens, G.EOF)

    @staticmethod
    def report_errors(tokens):
        errors = []
        for token in tokens:
            if not token.is_valid:
                error_text = HulkLexicographicError.UNKNOWN_TOKEN % token.lex
                errors.append(HulkLexicographicError(error_text, token.row, token.col))
            elif token.token_type == TokenType.UNTERMINATED_STRING:
                error_text = HulkLexicographicError.UNTERMINATED_STRING % token.lex
                errors.append(HulkLexicographicError(error_text, token.row, token.col))
        return errors

    def __call__(self, text):
        tokens = super().__call__(text)
        errors = self.report_errors(tokens)
        tokens = [ Token(str(math.pi), TokenType.NUMBER, token.row, token.col) if token.token_type == TokenType.PI else token 
                  for token in tokens ]
        tokens = [ Token(str(math.e), TokenType.NUMBER, token.row, token.col) if token.token_type == TokenType.EULER else token 
                  for token in tokens ]
        valid_tokens = [token for token in tokens if token.is_valid and
                           token.token_type not in [TokenType.SPACES, TokenType.ESCAPED_CHAR,
                                                    TokenType.UNTERMINATED_STRING]]
        return valid_tokens, errors