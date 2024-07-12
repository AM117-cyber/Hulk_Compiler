import math
import dill
import sys
from cmp.utils import Token
from lexer.hulk_token_types import TokenType
from lexer.lexer_error import HulkLexicographicError
from lexer.lexer_generator import Lexer
from lexer.regex_tokens import hulk_tokens
from grammar.hulk_grammar import G

class HulkLexer(Lexer):
    def __init__(self, use_cached = True):
        if use_cached:
            try:
                with open('lexer/hulk_lexer.pkl', 'rb') as automaton_pkl:
                    self.automaton = dill.load(automaton_pkl)
                self.eof = G.EOF
                with open('lexer/hulk_lexer_regexs.pkl', 'rb') as regexs_pkl:
                    self.regexs = dill.load(regexs_pkl)
            except:
                super().__init__(hulk_tokens, G.EOF)
        else:
            super().__init__(hulk_tokens, G.EOF)
            sys.setrecursionlimit(10000)

            with open('lexer/hulk_lexer.pkl', 'wb') as automaton_pkl:
                dill.dump(self.automaton, automaton_pkl)
            with open('lexer/hulk_lexer_regexs.pkl', 'wb') as regexs_pkl:
                dill.dump(self.regexs, regexs_pkl)

        

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