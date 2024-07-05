from cmp.pycompiler import Symbol
from cmp.pycompiler import NonTerminal
from cmp.pycompiler import Terminal
from cmp.pycompiler import EOF
from cmp.pycompiler import Sentence, SentenceList
from cmp.pycompiler import Epsilon
from cmp.pycompiler import Production
from cmp.pycompiler import Grammar
from cmp.utils import pprint, inspect

G = Grammar()

Program = G.NonTerminal('Program', True)

# ----------------------------------------------------------------------------------------------------------------
#                                       Definiendo los No Terminales
Type_function_list = G.NonTerminal('Type_function_list')
Expr_block, Expr_list, Expr_item_list, Expr, Simple_expr = G.NonTerminals('Expr_block Expr_list Expr_item_list Expr Simple_expr')
Or_expr, And_expr, Aritm_comp = G.NonTerminals('Or_expr And_expr Aritm_comp') 
Concat = G.NonTerminal('Concat')
Arithmetic, Term, Pow, Factor = G.NonTerminals('Arithmetic Term Pow Factor')
Conditional, Cond_other_case = G.NonTerminals('Conditional Cond_other_case')
Let_expr, Assignment = G.NonTerminals('Let_expr Assignment')
Destr_assig = G.NonTerminal('Destr_assig')
Atom, Call_func, Member = G.NonTerminals('Atom Call_func Member')
Variable, Params, Method_dec, Inline_form, Full_form, Func, Arguments = G.NonTerminals('Variable Params Method_dec Inline_form Full_form Func Arguments')
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
false, true, id_, num, let, in_, function_, string_ = G.Terminals('false true id num let in function string')
if_, elif_, else_  = G.Terminals('if elif else')
as_, is_ = G.Terminals('as is')
while_, for_ = G.Terminals('while for')
type_, inherits, new = G.Terminals('type inherits new')
protocol_, extends = G.Terminals('protocol extends')

# ----------------------------------------------------------------------------------------------------------------
#                                               Producciones
Program %= Type_function_list + Expr_item_list 

Type_function_list %= Func + Type_function_list
Type_function_list %= Type + Type_function_list
Type_function_list %= Protocol + Type_function_list
Type_function_list %= G.Epsilon

# Un bloque de expresiones es una lista de expresiones entre { }
Expr_block %= o_curly + Expr_list + c_curly

# Una lista de expresiones es un conjunto de expresiones de item list
Expr_list %= Expr_item_list + Expr_list 
Expr_list %= Expr_item_list

# Un elemento de una lista de expresiones puede ser una expresion seguida de un ';' o un bloque de expresiones
Expr_item_list %= Expr + semicolon 
Expr_item_list %= Expr_block

# Una expresion puede ser un bloque de expresiones o una expresion simple
Expr %= Expr_block
Expr %= Simple_expr

# Una expresion simple puede ser un condicional, una expresion let o un destructive assignment
Simple_expr %= Conditional
Simple_expr %= Let_expr
Simple_expr %= While_loop
Simple_expr %= For_loop
Simple_expr %= Destr_assig

Destr_assig %= Variable + destr_op + Expr
Destr_assig %= Or_expr 

Or_expr %= Or_expr + or_op + And_expr
Or_expr %= And_expr

And_expr %= And_expr + and_op + Check_type
And_expr %= Check_type

Check_type %= Check_type + is_ + Aritm_comp
Check_type %= Aritm_comp

Aritm_comp %= Aritm_comp + equal + Concat
Aritm_comp %= Aritm_comp + not_equal + Concat
Aritm_comp %= Aritm_comp + gth + Concat
Aritm_comp %= Aritm_comp + geth + Concat
Aritm_comp %= Aritm_comp + lth + Concat
Aritm_comp %= Aritm_comp + leth + Concat
Aritm_comp %= Concat

Concat %= Concat + concat_op + Arithmetic
Concat %= Concat + double_concat_op + Arithmetic
Concat %= Arithmetic 

Arithmetic %= Arithmetic + plus_op + Term 
Arithmetic %= Arithmetic + minus_op + Term 
Arithmetic %= Term

Term %= Term + mult_op + Pow
Term %= Term + div_op + Pow 
Term %= Term + mod_op + Pow
Term %= Pow

Pow %= Sign + pow_op + Pow
Pow %= Sign + double_star_op + Pow 
Pow %= Sign

Sign %= plus_op + Factor
Sign %= minus_op + Factor
Sign %= Factor

Factor %= not_op + Atom
Factor %= Atom

Atom %= o_par + Expr + c_par
Atom %= Expr_block
Atom %= false
Atom %= true
Atom %= Call_func
Atom %= Type_inst
Atom %= Vector
Atom %= Index_object
Atom %= id_
Atom %= Member
Atom %= num
Atom %= string_
Atom %= Cast_type

Conditional %= if_ + o_par + Expr + c_par +  Expr + Cond_other_case
Cond_other_case %= elif_ + o_par + Expr + c_par + Expr + Cond_other_case 
Cond_other_case %= else_ + Expr

Let_expr %= let + Assignment + in_ + Expr

Assignment %= Variable + assign_op + Expr + comma + Assignment
Assignment %= Variable + assign_op + Expr

Variable %= id_ + colon + id_
Variable %= id_

# Un parametro es una variable que recibe una funcion cuando es declarada
Params %= Variable + comma + Params
Params %= Variable 

Method_dec %= id_ + o_par + Params + c_par + colon + id_
Method_dec %= id_ + o_par + Params + c_par
Method_dec %= id_ + o_par + c_par + colon + id_
Method_dec %= id_ + o_par + c_par

Inline_form %= Method_dec + arrow + Simple_expr + semicolon

Full_form %= Method_dec + Expr_block + semicolon
Full_form %= Method_dec + Expr_block 

Func %= function_ + Inline_form
Func %= function_ + Full_form

# Un argumento es un valor que le pasamos a una funcion cuando se va a llamar
Arguments %= Expr + comma + Arguments
Arguments %= Expr

Call_func %= id_ + o_par + Arguments + c_par
Call_func %= id_ + o_par + c_par

Member %= Atom + dot + Call_func 
Member %= Atom + dot + id_

While_loop %= while_ + o_par + Expr + c_par + Expr

For_loop %= for_ + o_par + id_ + in_ + Expr + c_par + Expr

Type_block %= o_curly + Type_member_list + c_curly

Type_member_list %= Type_member_item + Type_member_list
Type_member_list %= G.Epsilon

Type_member_item %= Inline_form + semicolon
Type_member_item %= Full_form
Type_member_item %= Variable + assign_op + Expr + semicolon

Type %= type_ + Type_dec + Type_block
Type %= type_ + Type_dec + inherits + Type_dec + Type_block

Type_dec %= id_ + o_par + Params + c_par
Type_dec %= id_

Type_inst %= new + Call_func

Protocol_block %= o_curly + Method_dec_list + c_curly

Method_dec_list %= Method_dec + semicolon + Method_dec_list
Method_dec_list %= G.Epsilon

Protocol %= protocol_ + id_ + extends + id_ + Protocol_block
Protocol %= protocol_ + id_ + Protocol_block

Vector %= Vector_exp
Vector %= Vector_imp

Vector_exp %= o_square_bracket + Vector_item_list + c_square_bracket

Vector_item_list %= Expr + comma + Vector_item_list
Vector_item_list %= G.Epsilon

Vector_imp %= o_square_bracket + Expr + such_that_op + id_ + in_ + Expr + c_square_bracket

Index_object %= Atom + o_square_bracket + Expr + c_square_bracket

Cast_type %= Atom + as_ + id_

class Token:
    """
    Basic token class. 
    
    Parameters
    ----------
    lex : str
        Token's lexeme.
    token_type : Enum
        Token's type.
    """
    
    def __init__(self, lex, token_type):
        self.lex = lex
        self.token_type = token_type
    
    def __str__(self):
        return f'{self.token_type}: {self.lex}'
    
    def __repr__(self):
        return str(self)
    
test1 = '''type Person {
                age = 25;
                
                printAge(){
                    print(age);
                }
            }
            
            let x = new Person() in x.printAge();'''
tokens1 = [Token('type', type_), Token('Person', id_),Token('{', o_curly), 
            Token('age', id_), Token('=', assign_op), Token('25', num), Token(';', semicolon),
            Token('printAge', id_), Token('(', o_par), Token(')', c_par), Token('{', o_curly),
            Token('print', id_), Token('(', o_par), Token('age', id_), Token(')', c_par), Token(';', semicolon),
            Token('}', c_curly),
           Token('}', c_curly),
           Token('let', let), Token('x', id_), Token('=', assign_op), Token('new', new), Token('Person', id_), Token('(', o_par), Token(')', c_par), Token('in', in_), Token('x', id_), Token('.', dot), Token('printAge', id_), Token('(', o_par), Token(')', c_par), Token(';', semicolon)]
            

test2 = '''type Person{
                name = "John";
                age = 25;
                
                printName(){
                    print(name);
                }
            }
            
            let x = new Person() in if (x.name == "Jane") print("Jane") else print("John");'''
tokens2 = [Token('type', type_), Token('Person', id_),Token('{', o_curly),
            Token('name', id_), Token('=', assign_op), Token('"John"', string_), Token(';', semicolon),  
            Token('age', id_), Token('=', assign_op), Token('25', num), Token(';', semicolon),
            Token('printName', id_), Token('(', o_par), Token(')', c_par), Token('{', o_curly),
            Token('print', id_), Token('(', o_par), Token('name', id_), Token(')', c_par), Token(';', semicolon),
            Token('}', c_curly),
           Token('}', c_curly),
           Token('let', let), Token('x', id_), Token('=', assign_op), Token('new', new), Token('Person', id_), Token('(', o_par), Token(')', c_par), Token('in', in_), Token('if', if_), Token('(', o_par), Token('x', id_), Token('.', dot), Token('name', id_), Token('==', equal), Token('"Jane"', string_), Token(')', c_par), Token('print', id_), Token('(', o_par), Token('"Jane"', string_), Token(')', c_par), Token('else', else_), Token('print', id_), Token('(', o_par), Token('"John"', string_), Token(')', c_par), Token(';', semicolon)]

test3 = '''function Sort(A) => 
            let  aux = 0 in for (i in range(0, A.size()))
                for (j in range(i, A.size()))
                 if(A[j] < A[i])
                 {
                    aux := A[i];
                    A[i] := A[j];
                    A[j] := aux;
                    A;
                }
                else A;

            print(Sort([78, 12, 100, 0, 6, 9, 4.5]));'''
tokens3 = [Token('function', function_), Token('Sort', id_), Token('(', o_par), Token('A', id_), Token(')', c_par), Token('=>', arrow),
            Token('let', let), Token('aux', id_), Token('=', assign_op), Token('0', num), Token('in', in_), Token('for', for_), Token('(', o_par), Token('i', id_), Token('in', in_), Token('range', id_), Token('(', o_par), Token('0', num), Token(',', colon), Token('A', id_), Token('.', dot), Token('size', id_), Token('(', o_par), Token(')', c_par), Token(')', c_par), Token(')', c_par), 
            Token('for', for_), Token('(', o_par), Token('j', id_), Token('in', in_), Token('range', id_), Token('(', o_par), Token('i', id_), Token(',', colon), Token('A', id_), Token('.', dot), Token('size', id_), Token('(', o_par), Token(')', c_par), Token(')', c_par), Token(')', c_par), 
            Token('if', if_), Token('(', o_par), Token('A', id_), Token('[', o_square_bracket), Token('j', id_), Token(']', c_square_bracket), Token('<', lth), Token('A', id_), Token('[', o_square_bracket), Token('i', id_), Token(']', c_square_bracket), Token(')', c_par),
            Token('{', o_curly),
                Token('aux', id_), Token(':=', destr_op), Token('A', id_), Token('[', o_square_bracket), Token('i', id_), Token(']', c_square_bracket), Token(';', semicolon),
                Token('A', id_), Token('[', o_square_bracket), Token('i', id_), Token(']', c_square_bracket), Token(':=', destr_op), Token('A', id_), Token('[', o_square_bracket), Token('j', id_), Token(']', c_square_bracket),
                Token('A', id_), Token('[', o_square_bracket), Token('i', id_), Token(']', c_square_bracket), Token(':=', destr_op), Token('aux', id_), Token(';', semicolon),
                Token('A', id_), Token(';', semicolon),
            Token('}', c_square_bracket),
            Token('else', else_), Token('A', id_), Token(';'),
           Token('print', id_), Token('(', o_par), Token('Sort', id_), Token('(', o_par), Token('[', o_square_bracket), Token('78', num), Token(',', colon), Token('12', num), Token(',', colon), Token('100', num), Token(',', colon), Token('0', num), Token(',', colon), Token('6', num), Token(',', colon), Token('9', num), Token(',', colon), Token('4.5', num), Token(']', c_square_bracket), Token(')', c_par), Token(')', c_par), Token(';', semicolon)]