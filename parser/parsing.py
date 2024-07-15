from typing import List
from cmp.pycompiler import Grammar
from cmp.pycompiler import Item
from cmp.automata import State, lr0_formatter
from parser.utils import compute_firsts, compute_follows

class ParserError(Exception):
    def __init__(self, text, token_index):
        super().__init__(text)
        self.token_index = token_index

class Building_Table_Conflicts():
    def __init__(self, key, prev_value, new_value):
        self.key = key
        self.prev_value = prev_value
        self.new_value = new_value
# lo que se espera que esto haga es que cada estado tenga en el diccionario transitions(viene definido para el estado) 
# el estado al que corresponde ir cuando recibas el símbolo que está como key en el dict 
#  epsilon-transitions para el estado también van en un dict(epsilon_transitions) declarado en state
def build_LR0_automaton(G):
    assert len(G.startSymbol.productions) == 1, 'Grammar must be augmented'
    # se recibe una gramática aumentada
    start_production = G.startSymbol.productions[0]
    start_item = Item(start_production, 0)

    automaton = State(start_item, True)
    #el booleano que se pasa a state representa si es final o no, por eso en todos pasamos true

    pending = [ start_item ]
    visited = { start_item: automaton }

    while pending:
        current_item = pending.pop()
        if current_item.IsReduceItem: #si el punto está al final de la prod, es decir, se ha leído completa
            continue #deja ese estado así sin transición porque ya es un reduce, lo que indicará cuando termine el autómata que se debe reducir 
        # (Decide which transitions to add)
        next_symbol = current_item.NextSymbol
        if(next_symbol.IsNonTerminal):
            #agregamos las epsilon-transitions
            for prod in next_symbol.productions:
                prod_first_item = Item(prod, 0)
                #como visited es un diccionario que tiene como llave a los items 
                # creamos el item correspondiente a prod para ver si ya iniciamos el estado correspondiente
                if(not prod_first_item  in visited):
                    visited[prod_first_item] = State(prod_first_item, True)
                    pending.append(prod_first_item)
                visited[current_item].epsilon_transitions.add(visited[prod_first_item])
        next_item = current_item.NextItem()
        if(not next_item  in visited):
            visited[next_item] = State(next_item, True)
            pending.append(next_item)
        visited[current_item].add_transition(next_symbol.Name, visited[next_item])#debería usar los métodos de state???

        # if(next_symbol.IsNonTerminal):


            #si es no terminal se pone una epsilon_transition para toda su epsilon_clausure de primer nivel(no le sacas epsilon clausure a los que vienen después), que está dada por las producciones del next_symbol
            
            
            # for 
            # current_item.transitions[next_symbol] = State(current_item.NextItem, True)


        # foreach item in state if item.next_symbol is terminal c then add transitions[c] = item.next_item and create a state with the closure of that item
        # if it's non terminal Y then add transitions[Y] = item.next_item and epsilon_transitions[] = every production with Y -> .body


    return automaton







def build_deterministic_LR0_automaton(G):
    assert len(G.startSymbol.productions) == 1, 'Grammar must be augmented'

    start_production = G.startSymbol.productions[0]
    start_item = Item(start_production, 0)

    automaton = State(start_item, True)
    #el booleano que se pasa a state representa si es final o no, por eso en todos pasamos true
    automaton = State(tuple(automaton), True)
    pending = [ automaton ] # va a tener los estados con varios items dentro
    visited = { start_item: automaton }
    states_per_kernel_items = {start_item: automaton} # porque el único item kernel del estado inicial es la prod inicial con pos 0
    # los items kernels surgen de las transiciones hacia ti
    current_kernel_item = start_item
    while pending:
        # una vez sacado el estado de pending ya tiene sus kernel items, solo hay que agregar los no kernel(epsilon-transitions)
        current_state = pending.pop()
        
        current_kernel_states = []
        curr_state_per_symbol_transition = {}
        my_states = list(current_state.state)
        non_kernel_states = []
        while(my_states):
            state = my_states.pop()
            current_item = state.state
            if(current_item.IsReduceItem):
                continue
            next_symbol = current_item.NextSymbol
            count = len(non_kernel_states)
            non_kernel_states = get_non_kernels(non_kernel_states, next_symbol, [state.name for state in current_state.state])
            change = count != len(non_kernel_states)
            if(change):
                current_state.state = current_state.state + tuple(non_kernel_states)
                my_states = my_states + non_kernel_states
            #añadiendo transiciones para otros estados
            if(not next_symbol in curr_state_per_symbol_transition):
                new_state = State(tuple(State(current_item.NextItem(), True)), True)
                curr_state_per_symbol_transition[next_symbol] = (new_state,[current_item.NextItem()])
            else:
                #hay un estado al que me debo mover con este símbolo
                #luego a ese estado le agrego en sus kernel items el next_item correspondiente a mi current_item
                curr_state_per_symbol_transition[next_symbol][1].append(current_item.NextItem())
                curr_state_per_symbol_transition[next_symbol][0].state = curr_state_per_symbol_transition[next_symbol][0].state + tuple(State(current_item.NextItem(), True))
        #en este punto los estados hacia los que tengo una transición ya tienen todos sus kernel items
        for symbol in curr_state_per_symbol_transition.keys():
            kernel_items = tuple(curr_state_per_symbol_transition[symbol][1])
            if( kernel_items in states_per_kernel_items):
                #si los kernel items ya están en el diccionario la transición se añade al estado que está en el value correspondiente
                current_state.add_transition(symbol.Name, states_per_kernel_items[kernel_items])
            else:
                current_state.add_transition(symbol.Name, curr_state_per_symbol_transition[symbol][0])
                states_per_kernel_items[kernel_items] = curr_state_per_symbol_transition[symbol][0]
                pending.append(curr_state_per_symbol_transition[symbol][0])

    return automaton

def get_non_kernels(non_kernel_states, next_symbol,names):
    if(next_symbol.IsNonTerminal):
        for prod in next_symbol.productions:
            new_item = Item(prod, 0)
            new_state = State(new_item, True)
            if(not new_state.name in names): # para no tener los non kernel items repetidos
                non_kernel_states.append(new_state)
                names.append(new_state.name)
                if(not new_item.IsReduceItem):
                    get_non_kernels(non_kernel_states, new_item.NextSymbol, names)
    return non_kernel_states

        # if(next_symbol.IsNonTerminal):


            #si es no terminal se pone una epsilon_transition para toda su epsilon_clausure de primer nivel(no le sacas epsilon clausure a los que vienen después), que está dada por las producciones del next_symbol
            
            
            # for 
            # current_item.transitions[next_symbol] = State(current_item.NextItem, True)


        # foreach item in state if item.next_symbol is terminal c then add transitions[c] = item.next_item and create a state with the closure of that item
        # if it's non terminal Y then add transitions[Y] = item.next_item and epsilon_transitions[] = every production with Y -> .body
        # Your code here!!! (Add the decided transitions)
    # print(" after: ")
    # print(visited)








class ShiftReduceParser:
    SHIFT = 'SHIFT'
    REDUCE = 'REDUCE'
    OK = 'OK'
    
    def __init__(self, G, verbose=False):
        self.G = G
        self.verbose = verbose
        self.action = {}
        self.goto = {}
        self._build_parsing_table()
    
    def _build_parsing_table(self):
        raise NotImplementedError()

    def __call__(self, w):
        stack = [ 0 ]
        cursor = 0
        output = []
        operations = []

        while True:
            state = stack[-1]
            lookahead = w[cursor]
            if self.verbose: print(stack, '<---||--->', w[cursor:])
                
            # Your code here!!! (Detect error) 
            # Como para determinar la acción a realizar accedemos a un valor del diccionario action con llave state, lookahead 
            # tenemos que lanzar error si no existe valor para esta llave
            if((state, lookahead) not in self.action):
                # print("Automaton didn't recognize w")
                # print("Stopped at state: " + str(state) + " lookahead: " + str(lookahead))
                raise ParserError(f"Chain cannot be parsed, error at {w[cursor]}",cursor)
            action, tag = self.action[state, lookahead]

            operations.append(action)
            
            if(action == self.SHIFT):
                stack.append(tag) # asumiendo que tag es el estado al que me debo mover
                cursor +=1
            elif(action == self.REDUCE):
                # tag será la prod a aplicar
                # Saco de stacks tantos estados como la cantidad de símbolos en la parte derecha de la prod
                # print("Removing a state from stack per symbol in the right:")
                for symbol in tag.Right:
                    # print(symbol)
                    state = stack.pop()
                    # print(state)
                # goto me da el estado al que quieres que vaya
                try:
                    state_to_goto = self.goto[stack[-1], tag.Left]
                except:
                #     print("Automaton didn't recognize w")
                #     print("Stopped at state: " + state + " lookahead: " + lookahead)
                      raise ParserError(f"Chain cannot be parsed, error at {w[cursor]}",cursor)
                stack.append(state_to_goto)
                output.append(tag)
            elif(action == self.OK):
                stack.pop()
                return output, operations

class SLR1Parser(ShiftReduceParser):

    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar(True)
        firsts = compute_firsts(G)
        follows = compute_follows(G, firsts)
        errors = []
    
        for key, value in follows.items():
            # Format the string as "key : value"
            line_to_write = f"{key} : {value}\n"
            with open('follows.txt', 'a', encoding='utf-8') as file:
                file.write(line_to_write)

        
        automaton = build_deterministic_LR0_automaton(G)
        for i, node in enumerate(automaton):
        # Asigna el índice al nodo
            node.idx = i
        # Preparando el contenido a escribir
            # contenido = f"{i}\t\n\t {'\n\t '.join(str(x) for x in node.state)}\n"
    
        # Abre el archivo en modo de anexación ('a'), especificando la codificación UTF-8
            # with open('states.txt', 'a', encoding='utf-8') as archivo:
        # Escribe el contenido en el archivo
                # archivo.write(contenido)
                # archivo.close()
    
        for node in automaton:
            idx = node.idx
            for state in node.state:
                item = state.state
                if(item.IsReduceItem):
                    prod = item.production
                    if(prod.Left == G.startSymbol):
                        self._register(self.action,(idx,G.EOF), (self.OK, None), errors)
                    else:
                    # si he leído toda la prod X->alpha entonces por cada símbolo x en follow(X) agrego action[node.idx, x] = self.Reduce, prod
                    # como first y follow contienen terminales solamente lo agrego a action
                        for terminal in follows[item.production.Left]:
                            self._register(self.action, (idx, terminal), (self.REDUCE, item.production), errors)
                else:
                    next_symbol = item.NextSymbol
                    next_node = node.transitions[next_symbol.Name][0]
                    # para comprobar que la tabla se haya creado bien, pero no es un error relevante para el usuario
                    # try:
                    #     next_node = node.transitions[next_symbol.Name][0]
                    # except:
                        # print("Automaton doesn't have transition from state with item:" + str(item) + "with symbol: " + next_symbol.Name)
                    if(next_symbol.IsTerminal):

                        self._register(self.action, (idx, next_symbol), (self.SHIFT, next_node.idx), errors)
                    else:
                        self._register(self.goto, (idx, next_symbol), next_node.idx, errors)
        if(errors):
            for error in errors:
                print(f"There is a conflict at state {error.key}: current value is {error.prev_value} and tried to insert the new value {error.new_value}")
            raise Exception("Grammar is not SLR(1)")
    # - Feel free to use `self._register(...)`)
    @staticmethod
    def _register(table, key, value, errors):
        if(key not in table or table[key] == value):
        #assert key not in table or table[key] == value, 'Shift-Reduce or Reduce-Reduce conflict!!! '
            table[key] = value
        else:
            errors.append(Building_Table_Conflicts(key, table[key], value))
            # guardar todos los conflictos en la tabla y después imprimir posición de tabla con todos los posibles valores por cada pos que dio conflicto
            #raise Exception(f"Grammar is not SLR(1). There is a conflict at state {key}: current value is {table[key]} and tried to insert the new value {value}")
            # print("Error: " + str(table[key]) + " es el valor en tabla")
            # print("key: " + str(key) + " new value: " + str(value))

    