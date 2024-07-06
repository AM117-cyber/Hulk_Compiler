# Computes First(alpha), given First(Vt) and First(Vn) 
# alpha in (Vt U Vn)*
from cmp.utils import ContainerSet

# Computes First(alpha), given First(Vt) and First(Vn) 
# alpha in (Vt U Vn)*
def compute_local_first(firsts, alpha):
    first_alpha = ContainerSet()
    
    try:
        alpha_is_epsilon = alpha.IsEpsilon
    except:
        alpha_is_epsilon = False
    
    ###################################################
    # alpha == epsilon ? First(alpha) = { epsilon }
    ###################################################
    #                   <CODE_HERE>                   #
    ###################################################
    if(alpha_is_epsilon):
        first_alpha.set_epsilon(True)
        return first_alpha
    ###################################################
    # alpha = X1 ... XN
    # First(Xi) subconjunto First(alpha)
    # epsilon pertenece a First(X1)...First(Xi) ? First(Xi+1) subconjunto de First(X) y First(alpha)
    # epsilon pertenece a First(X1)...First(XN) ? epsilon pertence a First(X) y al First(alpha)
    ###################################################
    #                   <CODE_HERE>                   #
    ###################################################

    # Creo que se puede sacar los símbolos de sentence indexando por su definición de _get_item_

    #Iteramos por símbolos de alpha mientras deriven en epsilon y agregamos sus firsts al de alpha. Si todos derivan en epsilon entonces epsilon se incluye en alpha
    add_epsilon = True
    for symbol in alpha:
        first_symbol = firsts[symbol]
        first_alpha.update(first_symbol)
        if(not first_symbol.contains_epsilon):
            add_epsilon = False
            break
    
    if(add_epsilon):
        first_alpha.set_epsilon(True)

    # First(alpha)
    return first_alpha

# Computes First(Vt) U First(Vn) U First(alpha)
# P: X -> alpha
def compute_firsts(G):
    firsts = {}
    change = True
    
    # init First(Vt)
    for terminal in G.terminals:
        firsts[terminal] = ContainerSet(terminal)
        
    # init First(Vn)
    for nonterminal in G.nonTerminals:
        firsts[nonterminal] = ContainerSet()
    
    while change:
        change = False
        
        # P: X -> alpha
        for production in G.Productions:
            X = production.Left
            alpha = production.Right
            
            # get current First(X)
            first_X = firsts[X]
                
            # init First(alpha)
            try:
                first_alpha = firsts[alpha]
            except KeyError:
                first_alpha = firsts[alpha] = ContainerSet()
            
            # CurrentFirst(alpha)???
            local_first = compute_local_first(firsts, alpha)
            
            # update First(X) and First(alpha) from CurrentFirst(alpha)
            change |= first_alpha.hard_update(local_first)
            change |= first_X.hard_update(local_first)
                    
    # First(Vt) + First(Vt) + First(RightSides)
    return firsts

from itertools import islice

def compute_follows(G, firsts):
    follows = { }
    change = True
    
    local_firsts = {}
    
    # init Follow(Vn)
    for nonterminal in G.nonTerminals:
        follows[nonterminal] = ContainerSet()
    follows[G.startSymbol] = ContainerSet(G.EOF)
    
    while change:
        change = False
        
        # P: X -> alpha
        for production in G.Productions:
            X = production.Left
            alpha = production.Right
            follow_X = follows[X]

            if(not alpha.IsEpsilon):
                symbols = alpha._symbols
                index = len(symbols) -1
                index_is_last = True
                while(index >= 0):
                    current_symbol = symbols[index]
                    if(index_is_last):
                        if(current_symbol.IsNonTerminal):
                            change |= follows[current_symbol].update(follows[X])
                        index_is_last = False
                    
                    beta = symbols[index:]
                    
                    if not beta in local_firsts.keys():
                        for symbol in beta :
                            local_firsts[beta] = ContainerSet()
                            local_firsts[beta].hard_update(firsts[symbol])
                            if(not firsts[symbol].contains_epsilon):
                                break
                    if(index > 0):
                        # if(symbols[0].Name == 'Concat'):
                        #     print("d")
                        previous_symbol = symbols[index-1]
                        if(previous_symbol.IsNonTerminal):
                            change |= follows[previous_symbol].update(local_firsts[beta])
                        if(local_firsts[beta].contains_epsilon and previous_symbol.IsNonTerminal):
                            change |= follows[previous_symbol].update(follows[X])
                    index -= 1
            

            ###################################################
            # X -> zeta Y beta
            # First(beta) - { epsilon } subset of Follow(Y)
            # beta ->* epsilon or X -> zeta Y ? Follow(X) subset of Follow(Y)
            ###################################################
            #                   <CODE_HERE>                   #
            ###################################################

    # Follow(Vn)
    return follows
