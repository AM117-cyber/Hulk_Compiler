import pydot
from cmp.utils import ContainerSet

class NFA:
    def __init__(self, states, finals, transitions, start=0):
        self.states = states
        self.start = start
        self.finals = set(finals)
        self.map = transitions
        self.vocabulary = set()
        self.transitions = { state: {} for state in range(states) }
        
        for (origin, symbol), destinations in transitions.items():
            assert hasattr(destinations, '__iter__'), 'Invalid collection of states'
            self.transitions[origin][symbol] = destinations
            self.vocabulary.add(symbol)
            
        self.vocabulary.discard('')
        
    def epsilon_transitions(self, state):
        assert state in self.transitions, 'Invalid state'
        try:
            return self.transitions[state]['']
        except KeyError:
            return ()
            
    def graph(self):
        G = pydot.Dot(rankdir='LR', margin=0.1)
        G.add_node(pydot.Node('start', shape='plaintext', label='', width=0, height=0))

        for (start, tran), destinations in self.map.items():
            tran = 'ε' if tran == '' else tran
            G.add_node(pydot.Node(start, shape='circle', style='bold' if start in self.finals else ''))
            for end in destinations:
                G.add_node(pydot.Node(end, shape='circle', style='bold' if end in self.finals else ''))
                G.add_edge(pydot.Edge(start, end, label=tran, labeldistance=2))

        G.add_edge(pydot.Edge('start', self.start, label='', style='dashed'))
        return G

    def _repr_svg_(self):
        try:
            return self.graph().create_svg().decode('utf8')
        except:
            pass

class DFA(NFA):
    
    def __init__(self, states, finals, transitions, start=0):
        assert all(isinstance(value, int) for value in transitions.values())
        assert all(len(symbol) > 0 for origin, symbol in transitions)
        
        transitions = { key: [value] for key, value in transitions.items() }
        NFA.__init__(self, states, finals, transitions, start)
        self.current = start
        
    def _move(self, symbol):
        
        if symbol not in self.transitions[self.current].keys():
            return False
        
        self.current = self.transitions[self.current][symbol][0]
        return True

    
    def _reset(self):
        self.current = self.start
        
    def recognize(self, string):
        self._reset()
        for caract in string:
            if not self._move(caract):
                return False

        return self.current in self.finals       

# CONVIRTIENDO DE NFA a DFA
def move(automaton, states, symbol):
    moves = set()
    for state in states:
        if symbol not in automaton.transitions[state].keys():
            continue
        
        moves = moves.union(set(automaton.transitions[state][symbol]))
    
    return moves

def epsilon_closure(automaton, states):
    pending = [ s for s in states ] # equivalente a list(states) pero me gusta así :p
    closure = { s for s in states } # equivalente a  set(states) pero me gusta así :p
    
    while pending:
        state = pending.pop()
        closure.add(state)

        if '' in automaton.transitions[state].keys():
            for target in automaton.transitions[state]['']:
                pending.append(target)
                
    return ContainerSet(*closure)

def nfa_to_dfa(automaton):
    transitions = {}
    
    start = epsilon_closure(automaton, [automaton.start])
    start.id = 0
    start.is_final = any(s in automaton.finals for s in start)
    states = [ start ]
    
    pending = [ start ]
    while pending:
        state = pending.pop()
        
        for symbol in automaton.vocabulary:
            # Your code here
            # ...
            dfa_states = move(automaton, state, symbol)
            nfa_state = epsilon_closure(automaton, dfa_states)
            
            if len(nfa_state) == 0:
                continue

            if nfa_state not in states:
                nfa_state.id = len(states)
                nfa_state.is_final = any(s in automaton.finals for s in nfa_state)
                states.append(nfa_state)
                pending.append(nfa_state)
            else:
                nfa_state.id = states.index(nfa_state)
            
            try:
                transitions[state.id, symbol]
                assert False, 'Invalid DFA!!!'
            except KeyError:
                # Your code here
                transitions[state.id, symbol] = nfa_state.id
                pass
    
    finals = [ state.id for state in states if state.is_final ]
    dfa = DFA(len(states), finals, transitions)
    return dfa

