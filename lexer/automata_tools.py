from cmp.utils import DisjointSet
from lexer.automata import NFA, DFA

# UNION DE AUTOMATAS
def automata_union(a1, a2):
    transitions = {}
    
    start = 0
    d1 = 1
    d2 = a1.states + d1
    final = a2.states + d2
    
    for (origin, symbol), destinations in a1.map.items():
        ## Relocate a1 transitions ...
        # Your code here
        transitions[(origin + d1, symbol)]  = [dest + d1 for dest in destinations]

    for (origin, symbol), destinations in a2.map.items():
        ## Relocate a2 transitions ...
        # Your code here
        transitions[(origin + d2, symbol)]  = [dest + d2 for dest in destinations]
    
    ## Add transitions from start state ...
    # Your code here
    transitions[(0, '')]  = [d1, d2]
    
    ## Add transitions to final state ...
    # Your code here
    for state in range(0, a1.states):
        if state in a1.finals:
            transitions[(state + 1, '')] = [final]

    for state in range(0, a2.states):
        if state in a2.finals:
            transitions[(state + d2, '')] = [final]

    # transitions[(d2-1, '')]  = [final]
    # transitions[(final - 1, '')]  = [final]
            
    states = a1.states + a2.states + 2
    finals = { final }

    # print(transitions)
    # print(finals)
    
    return NFA(states, finals, transitions, start)

# CONCATENACION DE AUTOMATA
def automata_concatenation(a1, a2):
    transitions = {}
    
    start = 0
    d1 = 0
    d2 = a1.states + d1
    final = a2.states + d2
    
    for (origin, symbol), destinations in a1.map.items():
        ## Relocate a1 transitions ...
        # Your code here
        transitions[(origin, symbol)] = destinations

    for (origin, symbol), destinations in a2.map.items():
        ## Relocate a2 transitions ...
        # Your code here
        transitions[(origin + d2, symbol)] = [dest + d2 for dest in destinations]
    
    ## Add transitions since finals states' a1 to start state's a2 ...
    # Your code here
    for state in range(0, a1.states):
        if state in a1.finals:
            transitions[(state, '')] = [d2]

    ## Add transitions to final state ...
    for state in range(0, a2.states):
        if state in a2.finals:
            try:
                transitions[(state + d2, '')] += [final]
            except KeyError:
                # Your code here
                transitions[(state + d2, '')] = [final]
            
    states = a1.states + a2.states + 1
    finals = { final }

    # print(transitions)
    # print(finals)
    
    return NFA(states, finals, transitions, start)

# CLAUSURA DE UN AUTOMATA
def automata_closure(a1):
    transitions = {}
    
    start = 0
    d1 = 1
    final = a1.states + d1
    
    for (origin, symbol), destinations in a1.map.items():
        ## Relocate automaton transitions ...
        # Your code here
        transitions[(origin + d1, symbol)] = [dest + d1 for dest in destinations]
    
    ## Add transitions from start state ...
    # Your code here
    transitions[(start, '')] = [final]
    
    ## Add transitions to final state and to start state ...
    # Your code here
    for state in range(0, a1.states):
        if state in a1.finals:
            transitions[(state + d1, '')] = [final]

    transitions[(final, '')] = [d1]
            
    states = a1.states +  2
    finals = { final }
    
    # print(transitions)
    # print(finals)

    return NFA(states, finals, transitions, start)

# MINIMIZANDO EL DFA
def distinguish_states(group, automaton, partition):
    split = {}
    vocabulary = tuple(automaton.vocabulary)

    for member in group:
        # Your code here
        band = False
        repr_member = partition[member.value].representative.value

        for caract in vocabulary:
            try:
                item = automaton.transitions[member.value][caract][0]
            except KeyError:
                continue
            
            repr_item = partition[item].representative.value
            if  repr_item != repr_member:
                try:
                    split[repr_item].append(member.value)
                except KeyError:
                    split[repr_item] = [member.value]
                # if repr_item in split:
                #     split[repr_item].append(member.value) 
                # else:
                #     split[repr_item] = [member.value]
                band = True
                break

        if not band:
            try:
                split[repr_member].append(member.value)
            except KeyError:
                split[repr_member] = [member.value]
            # if repr_item in split:
            #     split[repr_member].append(member.value) 
            # else:
            #     split[repr_member] = [member.value]    

    return [ group for group in split.values()]
            
def state_minimization(automaton):
    partition = DisjointSet(*range(automaton.states))
    
    ## partition = { NON-FINALS | FINALS }
    # Your code here
    partition.merge([state for state in range(0, automaton.states) if state not in automaton.finals])
    partition.merge(automaton.finals)
    
    while True:
        new_partition = DisjointSet(*range(automaton.states))
        
        ## Split each group if needed (use distinguish_states(group, automaton, partition))
        # Your code here
        groups_aux = []
        for group in partition.groups:
            groups_aux.extend(distinguish_states(group, automaton, partition))

        for group in groups_aux:
            new_partition.merge(group)

        if len(new_partition) == len(partition):
            break

        partition = new_partition
        
    return partition

def automata_minimization(automaton):
    partition = state_minimization(automaton)
    
    states = [s for s in partition.representatives]
    
    transitions = {}
    for i, state in enumerate(states):
        ## origin = ???
        # Your code here
        origin = state.value

        for symbol, destinations in automaton.transitions[origin].items():
            # Your code here
            repr_dest = partition[destinations[0]].representative
            dest = states.index(repr_dest)
            
            try:
                transitions[i,symbol]
                assert False
            except KeyError:
                # Your code here
                transitions[(i, symbol)] = dest
                pass
    
    ## finals = ???
    ## start  = ???
    # Your code here
    finals = [states.index(partition[s].representative) for s in range(0, automaton.states) if s in automaton.finals]
    start = states.index(partition[0].representative)

    return DFA(len(states), finals, transitions, start)

