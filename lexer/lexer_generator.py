from cmp.automata import State
from cmp.utils import Token, UnknownToken
from lexer.regex import Regex

class Lexer:
    def __init__(self, table, eof):
        self.eof = eof
        self.regexs = self._build_regexs(table)
        self.automaton = self._build_automaton()
    
    def _build_regexs(self, table):
        regexs = []
        for n, (token_type, regex) in enumerate(table):
            # Your code here!!!
            # - Remember to tag the final states with the token_type and priority.
            # - <State>.tag might be useful for that purpose ;-)
            regex_item = Regex(regex)
            automata, states = State.from_nfa(regex_item.automaton, True)
            for state in states:
                if state.final:
                    state.tag = n, token_type

            # pending = [automata]
            # visited = []
            # while pending:
            #     current = pending.pop()
            #     visited.append(current)
            #     if automata.final:
            #         automata.tag = n, token_type
            #         print(f'Tag {automata.tag}')

            #     for zz, state in automata.transitions.items():
            #         print(f'Simbolo {zz} y estado {state}')
            #         for s in state:
            #             if s not in visited:
            #                 pending.append(s)
                            
            #     for state in automata.epsilon_transitions:
            #         if state not in visited:
            #             pending.append(state)

            regexs.append(automata)

        return regexs
    
    def _build_automaton(self):
        start = State('start')
        # Your code here!!!
        for regex in self.regexs:
            start.add_epsilon_transition(regex)

        return start.to_deterministic()
    
        
    def _walk(self, string, row, col):
        state = self.automaton
        final = state if state.final else None
        final_lex = lex = ''
        
        states = state.state
        for symbol in string:
            # Your code here!!!
            if symbol == '\n':
                if final_lex == '':
                    final_lex = ' '
                row += 1
                col = 1
                return final, final_lex, row, col            
            lex = lex + symbol
            states = state.move_by_state(symbol, *states)
            if len(states):
                minx = len(self.regexs)+1
                for st in states:
                    if st.final and st.tag[0] is not None and st.tag[0] < minx:
                        minx = st.tag[0]
                        final = st
                        final_lex = lex
            else:
                break
        
        col += len(final_lex)
        return final, final_lex, row, col
    
    def _tokenize(self, text):
        # Your code here!!!
        string = text
        row = col = 1
        while len(string) > 0:
            state, lex, row_, col_ = self._walk(string, row, col)
            string = string[len(lex):]
            if lex.strip() == '':
                row = row_
                col = col_
                continue
            else:
                yield lex, state.tag[1], row, col
                col = col_

        yield '$', self.eof, row, col
    
    def __call__(self, text):
        return [ Token(lex, ttype, row, col) if ttype is not None else UnknownToken(lex, row, col) for lex, ttype, row, col in self._tokenize(text) ]
    
