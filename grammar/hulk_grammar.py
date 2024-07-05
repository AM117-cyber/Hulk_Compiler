from cmp.pycompiler import Grammar
from grammar.ast_nodes import *
G = Grammar()

Program = G.NonTerminal('Program', True)

# ----------------------------------------------------------------------------------------------------------------
#                                       Definiendo los No Terminales
Type_function_list = G.NonTerminal('Type_function_list')
Expr_block, Expr_list, Expr_item_list, Expr = G.NonTerminals('Expr_block Expr_list Expr_item_list Expr')
Or_expr, And_expr, Aritm_comp = G.NonTerminals('Or_expr And_expr Aritm_comp') 
Concat = G.NonTerminal('Concat')
Arithmetic, Term, Pow, Factor = G.NonTerminals('Arithmetic Term Pow Factor')
Conditional, Cond_other_case = G.NonTerminals('Conditional Cond_other_case')
Let_expr, Assignment = G.NonTerminals('Let_expr Assignment')
Destr_assig = G.NonTerminal('Destr_assig')
Atom, Call_func, Member = G.NonTerminals('Atom Call_func Member')
Variable, Params, Method_signature, Inline_form, Full_form, Func, Arguments = G.NonTerminals('Variable Params Method_signature Inline_form Full_form Func Arguments')
While_loop, For_loop = G.NonTerminals('While_loop For_loop')
Cast_type = G.NonTerminal('Cast_type')
Check_type = G.NonTerminal('Check_type')
Sign = G.NonTerminal('Sign')
Type_block, Type_member_list, Type_member_item, Type, Type_dec, Type_inst = G.NonTerminals('Type_block Type_member_list Type_member_item Type Type_dec Type_inst')
Protocol_block, Method_dec_list, Protocol = G.NonTerminals('Protocol_block Method_dec_list Protocol')
Vector, Vector_exp, Vector_imp, Vector_item_list, Index_object = G.NonTerminals('Vector Vector_exp Vector_imp Vector_item_list Index_object')

# ----------------------------------------------------------------------------------------------------------------
#                                       Definiendo los Terminales
o_curly, c_curly, semicolon, o_par, c_par, comma, colon, dot, destr_op, arrow, o_square_bracket, c_square_bracket, such_that_op = G.Terminals('{ } ; ( ) , : . := => [ ] ||')
or_op, and_op, equal, not_equal, gth, geth, lth, leth, not_op, assign_op = G.Terminals('| & == != > >= < <= ! =')
concat_op, double_concat_op = G.Terminals('@ @@')
plus_op, minus_op, mult_op, div_op, pow_op, double_star_op, mod_op = G.Terminals('+ - * / ^ ** %')
bool_, id_, num, let, in_, function_, string_ = G.Terminals('bool id num let in function string')
if_, elif_, else_  = G.Terminals('if elif else')
as_, is_ = G.Terminals('as is')
while_, for_ = G.Terminals('while for')
type_, inherits, new = G.Terminals('type inherits new')
protocol_, extends = G.Terminals('protocol extends')

# ----------------------------------------------------------------------------------------------------------------
# 
#                                               Producciones

#------------------------------------------------Hulk_Program-------------------------------------------------------------------
#Un programa en Hulk tiene un conjunto de declaraciones de tipos, protocolos y funciones y una única expresión

Program %= Type_function_list + Expr_item_list, lambda h, s: ProgramNode(s[1],s[2])

Type_function_list %= Func + Type_function_list, lambda h,s: [s[1]] + s[2]
Type_function_list %= Type + Type_function_list, lambda h, s: [s[1]] + s[2]
Type_function_list %= Protocol + Type_function_list, lambda h, s: [s[1]] + s[2]
Type_function_list %= G.Epsilon, lambda h, s: []
#----------------------------------------------------Declarations-------------------------------------------------------------------

#------------------------------------------------Function_Declaration-------------------------------------------------------------------

# Un parametro es una variable que recibe una funcion cuando es declarada
Params %= id_ + comma + Params, lambda h, s: [(s[1],None)]+s[3]
Params %= id_, lambda h, s: [(s[1],None)]
Params %= id_ + colon + id_ + comma + Params, lambda h, s: [(s[1],s[3])]+s[5]
Params %= id_ + colon + id_, lambda h, s: [(s[1],s[3])]

Method_signature %= id_ + o_par + Params + c_par + colon + id_, lambda h, s: MethodSignatureNode(s[1],s[3],s[6])
Method_signature %= id_ + o_par + Params + c_par, lambda h, s: MethodSignatureNode(s[1],s[3])
Method_signature %= id_ + o_par + c_par + colon + id_, lambda h, s: MethodSignatureNode(s[1],[],s[5])
Method_signature %= id_ + o_par + c_par, lambda h, s: MethodSignatureNode(s[1],[])
#El tercer parámetro por defecto es None

Inline_form %= Method_signature + arrow + Expr + semicolon, lambda h, s: MethodDeclarationNode(s[1],s[3])

Full_form %= Method_signature + Expr_block + semicolon, lambda h, s: MethodDeclarationNode(s[1],s[2])
Full_form %= Method_signature + Expr_block, lambda h, s: MethodDeclarationNode(s[1],s[2])

Func %= function_ + Inline_form, lambda h,s: FunctionDeclarationNode(s[2])
Func %= function_ + Full_form, lambda h,s: FunctionDeclarationNode(s[2])

#------------------------------------------------Type_Declaration-------------------------------------------------------------------

Type %= type_ + Type_dec + Type_block, lambda h,s: TypeDeclarationNode(s[2],s[3])
# Por defecto el siguiente argumento es None
Type %= type_ + Type_dec + inherits + id_ + Type_block, lambda h,s: TypeDeclarationNode(s[2], s[5], s[4]) 
#Por defecto el último argumento es []
Type %= type_ + Type_dec + inherits + id_ + o_par + Arguments + c_par + Type_block, lambda h,s: TypeDeclarationNode(s[2],s[8],s[4],s[6])

Type_dec %= id_ + o_par + Params + c_par, lambda h,s: TypeConstructorSignatureNode(s[1],s[3])
Type_dec %= id_, lambda h,s: TypeConstructorSignatureNode(s[1])
#Por defecto el segundo argumento es []

Type_block %= o_curly + Type_member_list + c_curly, lambda h, s: s[2]

Type_member_list %= Type_member_item + Type_member_list, lambda h,s: [s[1]] + s[2]
Type_member_list %= G.Epsilon, lambda h,s: []

Type_member_item %= Inline_form, lambda h,s: s[1]
Type_member_item %= Full_form, lambda h,s: s[1]
Type_member_item %= id_ + assign_op + Expr + semicolon, lambda h,s: TypeAttributeNode(s[1],s[3]) 
Type_member_item %= id_ + colon + id_ + assign_op + Expr + semicolon, lambda h,s: TypeAttributeNode(s[1],s[5],s[3]) 

#------------------------------------------------Protocol_Declaration-------------------------------------------------------------------

Protocol %= protocol_ + id_ + extends + id_ + Protocol_block, lambda h,s: ProtocolDeclarationNode(s[2],s[5],s[4])
Protocol %= protocol_ + id_ + Protocol_block, lambda h,s: ProtocolDeclarationNode(s[2],s[3])
#Tercer parámetro None

Protocol_block %= o_curly + Method_dec_list + c_curly, lambda h,s: s[2]

Method_dec_list %= Method_signature + semicolon + Method_dec_list, lambda h, s: [s[1]]+s[3]
Method_dec_list %= G.Epsilon, lambda h, s: []

#------------------------------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------Expressions-------------------------------------------------------------------

Expr %= Conditional, lambda h, s: s[1]
Expr %= Let_expr, lambda h, s: s[1]
Expr %= While_loop, lambda h, s: s[1]
Expr %= For_loop, lambda h, s: s[1]
Expr %= Destr_assig, lambda h, s: s[1]
#----------------------------------------------------Conditional-------------------------------------------------------------------

Conditional %= if_ + o_par + Expr + c_par +  Expr + Cond_other_case, lambda h, s: ConditionalNode([(s[3],s[5])]+s[6]) 
Cond_other_case %= elif_ + o_par + Expr + c_par + Expr + Cond_other_case, lambda h, s: [(s[3],s[5])]+s[6]
Cond_other_case %= else_ + Expr, lambda h, s: [(None,s[2])]

#-------------------------------------------------------LetIn-------------------------------------------------------------------

Let_expr %= let + Assignment + in_ + Expr, lambda h, s: LetInNode(s[2],s[4])

Assignment %= id_ + assign_op + Expr + comma + Assignment, lambda h, s: [VarDeclarationNode(s[1],s[3])]+s[5]
Assignment %= id_ + assign_op + Expr, lambda h, s: [VarDeclarationNode(s[1],s[3])]
Assignment %= id_ + colon + id_ + assign_op + Expr + comma + Assignment, lambda h, s: [VarDeclarationNode(s[1],s[5],s[3])]+s[7]
Assignment %= id_ + colon + id_ + assign_op + Expr, lambda h, s: [VarDeclarationNode(s[1],s[5],s[3])]

#--------------------------------------------------------Loops-------------------------------------------------------------------

While_loop %= while_ + o_par + Expr + c_par + Expr, lambda h ,s: WhileNode(s[3],s[5]) 

For_loop %= for_ + o_par + id_ + in_ + Expr + c_par + Expr, lambda h ,s: ForNode(s[3],s[5],s[7])

#--------------------------------------------------------Destructive-Assignment-------------------------------------------------------------------

Destr_assig %= id_ + destr_op + Expr, lambda h, s: DestrNode(s[1], s[3])
Destr_assig %= Atom + dot + id_ + destr_op + Expr, lambda h,s: DestrNode(CallTypeAttributeNode(s[1], s[3]), s[5])
Destr_assig %= Or_expr, lambda h, s: s[1]

#-------------------------------------------------Boolean-Expressions-------------------------------------------------------------------

Or_expr %= Or_expr + or_op + And_expr, lambda h,s : OrNode(s[1],s[3])
Or_expr %= And_expr, lambda h, s: s[1]

And_expr %= And_expr + and_op + Check_type, lambda h,s : AndNode(s[1],s[3])
And_expr %= Check_type, lambda h, s: s[1]

Check_type %= Check_type + is_ + Aritm_comp, lambda h,s : CheckTypeNode(s[1],s[3])
Check_type %= Aritm_comp, lambda h, s: s[1]

Aritm_comp %= Aritm_comp + equal + Concat, lambda h,s : EqualNode(s[1],s[3])
Aritm_comp %= Aritm_comp + not_equal + Concat, lambda h,s : NotEqualNode(s[1],s[3])
Aritm_comp %= Aritm_comp + gth + Concat, lambda h,s : GreaterNode(s[1],s[3])
Aritm_comp %= Aritm_comp + geth + Concat, lambda h,s : GreaterEqualNode(s[1],s[3])
Aritm_comp %= Aritm_comp + lth + Concat, lambda h,s : LessNode(s[1],s[3])
Aritm_comp %= Aritm_comp + leth + Concat, lambda h,s : LessEqualNode(s[1],s[3])
Aritm_comp %= Concat, lambda h, s: s[1]

#---------------------------------------------------String-Expressions-------------------------------------------------------------------

Concat %= Concat + concat_op + Arithmetic, lambda h,s: ConcatNode(s[1],s[3])
Concat %= Concat + double_concat_op + Arithmetic, lambda h,s: DoubleConcatNode(s[1],s[3]) 
Concat %= Arithmetic, lambda h, s: s[1]

#--------------------------------------------------Arithmetic-Expressions-------------------------------------------------------------------

Arithmetic %= Arithmetic + plus_op + Term, lambda h,s: PlusNode(s[1],s[3]) 
Arithmetic %= Arithmetic + minus_op + Term, lambda h,s: MinusNode(s[1],s[3]) 
Arithmetic %= Term, lambda h, s: s[1]

Term %= Term + mult_op + Pow, lambda h,s: MultNode(s[1],s[3]) 
Term %= Term + div_op + Pow, lambda h,s: DivNode(s[1],s[3]) 
Term %= Term + mod_op + Pow, lambda h,s: ModNode(s[1],s[3]) 
Term %= Pow, lambda h, s: s[1]

Pow %= Sign + pow_op + Pow, lambda h,s: PowNode(s[1],s[3])
Pow %= Sign + double_star_op + Pow, lambda h,s: PowNode(s[1],s[3])
Pow %= Sign, lambda h, s: s[1]

Sign %= plus_op + Factor, lambda h,s: PositiveNode(s[2])
Sign %= minus_op + Factor, lambda h,s: NegativeNode(s[2])
Sign %= Factor, lambda h, s: s[1]

Factor %= not_op + Atom,  lambda h,s: NotNode(s[2]) 
Factor %= Atom, lambda h, s: s[1]
#---------------------------------------------------------Atoms-------------------------------------------------------------------

Atom %= o_par + Expr + c_par, lambda h, s: s[2]
Atom %= Expr_block, lambda h,s : s[1]
Atom %= bool_, lambda h,s : BooleanNode(s[1])
Atom %= Call_func, lambda h,s : s[1]
Atom %= Type_inst, lambda h,s : s[1]
Atom %= Vector, lambda h,s : s[1]
Atom %= Index_object, lambda h,s : s[1]
Atom %= id_, lambda h,s : VarNode(s[1])
Atom %= Member, lambda h,s : s[1]
Atom %= num, lambda h,s : NumberNode(s[1])
Atom %= string_, lambda h,s : StringNode(s[1])
Atom %= Cast_type, lambda h,s : s[1]

#---------------------------------------------------Expression-Block-------------------------------------------------------------------

# Un bloque de expresiones es una lista de expresiones entre { }
Expr_block %= o_curly + Expr_list + c_curly, lambda h, s : ExpressionBlockNode(s[2])

# Una lista de expresiones es un conjunto de expresiones de item list
Expr_list %= Expr_item_list + Expr_list, lambda h, s: [s[1]] + s[2]
Expr_list %= Expr_item_list, lambda h, s: [s[1]]

# Un elemento de una lista de expresiones puede ser una expresion seguida de un ';' o un bloque de expresiones
Expr_item_list %= Expr + semicolon, lambda h, s: s[1]

#--------------------------------------------------Function_Call-------------------------------------------------------------------

Call_func %= id_ + o_par + Arguments + c_par, lambda h, s: CallFuncNode(s[1],s[3])
Call_func %= id_ + o_par + c_par, lambda h,s: CallFuncNode(s[1],[])

# Un argumento es un valor que le pasamos a una funcion cuando se va a llamar
Arguments %= Expr + comma + Arguments, lambda h,s: [s[1]] + s[3]
Arguments %= Expr, lambda h,s: [s[1]]

#-------------------------------------------------Type-Instantiation-------------------------------------------------------------------

Type_inst %= new + Call_func, lambda h,s: TypeInstantiationNode(s[2]) #OJO

#--------------------------------------------------------Vector-------------------------------------------------------------------

Vector %= Vector_exp, lambda h,s: s[1]
Vector %= Vector_imp, lambda h,s: s[1]

#Forma explícita
Vector_exp %= o_square_bracket + Vector_item_list + c_square_bracket, lambda h,s: ExplicitVectorNode(s[2])
Vector_exp %= o_square_bracket + c_square_bracket,lambda h,s: ExplicitVectorNode()
#[] por defecto

Vector_item_list %= Expr + comma + Vector_item_list, lambda h,s: [s[1]]+s[3]
Vector_item_list %= Expr,lambda h,s: [s[1]]

#Forma implícita
Vector_imp %= o_square_bracket + Expr + such_that_op + id_ + in_ + Expr + c_square_bracket, lambda h,s: ImplicitVectorNode(s[2],s[4],s[6])
#---------------------------------------------------Index-Object--------------------------------------------------------------

Index_object %= Atom + o_square_bracket + Expr + c_square_bracket, lambda h,s: IndexObjectNode(s[1],s[3])

#----------------------------------------------Call_Method-or-Type-Attribute------------------------------------------------------------------

Member %= Atom + dot + Call_func, lambda h,s: CallMethodNode(s[1],s[3])
Member %= Atom + dot + id_, lambda h,s: CallTypeAttributeNode(s[1],s[3])

#-----------------------------------------------------Cast_Type-------------------------------------------------------------------

Cast_type %= Atom + as_ + id_, lambda h,s: CastTypeNode(s[1],s[3]) 
#------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------
