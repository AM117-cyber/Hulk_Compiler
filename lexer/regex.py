from parser.evaluation import evaluate_reverse_parse
from lexer.automata import nfa_to_dfa
from lexer.automata_tools import automata_minimization
from lexer.regex_grammar import pipe, star, opar, cpar, epsilon, symbol, G_
from parser.parsing import SLR1Parser
from cmp.utils import Token

class Regex:
    def __init__(self, regex):
        self.tokens = self.regex_tokenizer(regex, G_)
        self.regex_parser = SLR1Parser(G_)
        self.ast = self.get_regex_ast()
        self.automaton = self.get_automaton()

    def regex_tokenizer(self, text, G, skip_whitespaces=True):
        tokens = []
        # > fixed_tokens = ???
        # Your code here!!!
        fixed_tokens = {
            '|'       :   Token( '|', pipe  ),
            '*'       :   Token( '*', star  ),
            '('       :   Token( '(', opar  ),
            ')'       :   Token( ')', cpar  ),
            'ε'       :   Token( 'ε', epsilon   )
        }

        before_backslash = False

        for char in text:
            if skip_whitespaces and char.isspace():
                tokens.append(Token(' ', symbol))
                continue
            # Your code here!!!
            if char != '\\' or before_backslash:
                if before_backslash:
                    tokens.append(Token(char, symbol))
                else:
                    if char in fixed_tokens:
                        tokens.append(fixed_tokens[char])
                    else:
                        tokens.append(Token(char, symbol))
                before_backslash = False
            else:
                before_backslash = True
        
        tokens.append(Token('$', G.EOF))
        return tokens
    
    def get_regex_ast(self):
        parse, operations, build_table_errors = self.regex_parser([t.token_type for t in self.tokens])
        if build_table_errors:
            print("Grammar is not SLR(1)")
            for err in build_table_errors:
                print(f"There is a conflict at state {err.key}: current value is {err.prev_value} and tried to insert the new value {err.new_value}")
            raise Exception()
        ast = evaluate_reverse_parse(parse, operations, self.tokens)
        
        return ast
    
    def get_automaton(self):
        automata = self.ast.evaluate()
        automata = nfa_to_dfa(automata)
        automata = automata_minimization(automata)

        return automata