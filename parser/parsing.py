from typing import List
from cmp.pycompiler import Grammar
from cmp.pycompiler import Item
from cmp.automata import State, lr0_formatter

class ParserError(Exception):
    def __init__(self, text, token_index):
        super().__init__(text)
        self.token_index = token_index


# lo que se espera que esto haga es que cada estado tenga en el diccionario transitions(viene definido para el estado) 
# el estado al que corresponde ir cuando recibas el símbolo que está como key en el dict 
#  epsilon-transitions para el estado también van en un dict(epsilon_transitions) declarado en state
def build_LR0_automaton(G):
    # assert len(G.startSymbol.productions) == 1, 'Grammar must be augmented'
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
                raise ParserError("Chain cannot be parsed", cursor)
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
                      raise ParserError("Chain cannot be parsed", cursor)
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
    
        # for key, value in follows.items():
        #     # Format the string as "key : value"
        #     line_to_write = f"{key} : {value}\n"
        #     with open('output.txt', 'a', encoding='utf-8') as file:
        #         file.write(line_to_write)

        
        automaton = build_LR0_automaton(G).to_deterministic()
        # for i, node in enumerate(automaton):
        # # Preparando el contenido a escribir
        #     contenido = f"{i}\t\n\t {'\n\t '.join(str(x) for x in node.state)}\n"
    
        # # Abre el archivo en modo de anexación ('a'), especificando la codificación UTF-8
        #     with open('salida.txt', 'a', encoding='utf-8') as archivo:
        # # Escribe el contenido en el archivo
        #         archivo.write(contenido)
        #         archivo.close()
    
        # # Asigna el índice al nodo
        #     node.idx = i


        for node in automaton:
            idx = node.idx
            for state in node.state:
                item = state.state
                if(item.IsReduceItem):
                    prod = item.production
                    if(prod.Left == G.startSymbol):
                        self._register(self.action,(idx,G.EOF), (self.OK, None))
                    else:
                    # si he leído toda la prod X->alpha entonces por cada símbolo x en follow(X) agrego action[node.idx, x] = self.Reduce, prod
                    # como first y follow contienen terminales solamente lo agrego a action
                        for terminal in follows[item.production.Left]:
                            self._register(self.action, (idx, terminal), (self.REDUCE, item.production))
                else:
                    next_symbol = item.NextSymbol
                    next_node = node.transitions[next_symbol.Name][0]
                    # para comprobar que la tabla se haya creado bien, pero no es un error relevante para el usuario
                    # try:
                    #     next_node = node.transitions[next_symbol.Name][0]
                    # except:
                        # print("Automaton doesn't have transition from state with item:" + str(item) + "with symbol: " + next_symbol.Name)
                    if(next_symbol.IsTerminal):

                        self._register(self.action, (idx, next_symbol), (self.SHIFT, next_node.idx))
                    else:
                        self._register(self.goto, (idx, next_symbol), next_node.idx)
    # - Feel free to use `self._register(...)`)
    @staticmethod
    def _register(table, key, value):
        if(key not in table or table[key] == value):
        #assert key not in table or table[key] == value, 'Shift-Reduce or Reduce-Reduce conflict!!! '
            table[key] = value
        else:
            # guardar todos los conflictos en la tabla y después imprimir posición de tabla con todos los posibles valores por cada pos que dio conflicto
            raise Exception(f"Grammar is not SLR(1). There is a conflict at state {key}: table[{key}] = {table[key]} and tried to insert the new value {value}")
            print("Error: " + str(table[key]) + " es el valor en tabla")
            print("key: " + str(key) + " new value: " + str(value))

    