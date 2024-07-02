from cmp.pycompiler import Grammar
from lexer.regex_ast import UnionNode, ConcatNode, ClosureNode, SymbolNode, EpsilonNode

G_ = Grammar()

E = G_.NonTerminal('E', True)
T, F, A = G_.NonTerminals('T F A')
pipe, star, opar, cpar, symbol, epsilon = G_.Terminals('| * ( ) symbol ε')

# > PRODUCTIONS???
# Your code here!!!
E %= E + pipe + T, lambda h, s: UnionNode(s[1],s[3])
E %= T, lambda h, s: s[1]

T %= T + F, lambda h, s: ConcatNode(s[1], s[2])
T %= F, lambda h,s: s[1]

F %= A + star, lambda h, s: ClosureNode(s[1])
F %= A, lambda h, s: s[1]

A %= opar + E + cpar, lambda h, s: s[2]
A %= symbol, lambda h, s: SymbolNode(s[1])
A %= epsilon, lambda h, s: EpsilonNode(s[1])
