import subprocess
import sys
import os
from pathlib import Path

from cmp.errors import HulkIOError
from grammar.format_visitor import FormatVisitor
from grammar.hulk_grammar import G
from lexer.hulk_lexer import HulkLexer
from parser.evaluation import evaluate_reverse_parse
from parser.hulk_parser import HulkParser
from semantic_checking.type_builder import TypeBuilder
from semantic_checking.type_checker import TypeChecker
from semantic_checking.type_collector import TypeCollector
from tables.cache import *
from tree_interpreter.interpreter import Interpreter

text ='''function tan(x: Number): Number => sin(x) / cos(x);
function cot(x) => 1 / tan(x);
function operate(x, y) {
    print(x + y);
    print(x - y);
    print(x * y);
    print(x / y);
}
function fib(n) => if (n == 0 | n == 1) 1 else fib(n-1) + fib(n-2);
function fact(x) => let f = 1 in for (i in range(1, x+1)) f := f * i;
function gcd(a, b) => while (a > 0)
        let m = a % b in {
            b := a;
            a := m;
        };
protocol Hashable {
    hash(): Number;
}
protocol Equatable extends Hashable {
    equals(other: Object): Boolean;
}
protocol Iterable {
    next() : Boolean;
    current() : Object;
}
type Range(min:Number, max:Number) {
    min = min;
    max = max;
    current = min - 1;

    next(): Boolean => (self.current := self.current + 1) < self.max;
    current(): Number => self.current;
}
type Point(x,y) {
    x = x;
    y = y;

    getX() => self.z := z;
    getY() => self.y;

    setX(x) => self.x := x;
    setY(y) => self.y := y;
}

type PolarPoint(phi, rho) inherits Point(rho * sin(phi), rho * cos(phi)) {
    rho() => sqrt(self.getX() ^ 2 + self.getY() ^ 2); 
}


type Knight inherits Person {
    name() => "Sir" @@ base();
}
type Person(firstname, lastname) {
    firstname = firstname;
    lastname = lastname;

    name() => self.firstname @@ self.lastname;
    hash() : Number {
        5;
    }
}
type Superman {
}
type Bird {
}
type Plane {
}
type A {
    hello() => print("A");
}

type B inherits A {
    hello() => print("B");
}

type C inherits A {
    hello() => print("C");
}

type wacamole{
    y = 0;
    f() {
        self.y:=12;
        self := new A(); 
    }
    g(a,b,a) {
        self.y:=12;
        self := new A(); 
    }
    f() {
        print("esto da error malditasea");
    }
}


{
    42;
    print(42);
    print((((1 + 2) ^ 3) * 4) / 5);
    print("Hello World");
    print("The message is \\"Hello World\\"");
    print("The meaning of life is " @ 42);
    print(sin(2 * PI) ^ 2 + cos(3 * PI / log(4, 64)));
    {
        print(42);
        print(sin(PI/2));
        print("Hello World");
    };

    
    print(tan(PI) ** 2 + cot(PI) ** 2);

    let msg = "Hello World" in print(msg);
    let number = 42, text = "The meaning of life is" in
        print(text @ number);
    let number = 42 in
        let text = "The meaning of life is" in
            print(text @ number);
    let number = 42 in (
        let text = "The meaning of life is" in (
                print(text @ number)
            )
        );
    let a = 6, b = a * 7 in print(b);
    let a = 6 in
        let b = a * 7 in
            print(b);
    let a = 5, b = 10, c = 20 in {
        print(a+b);
        print(b*c);
        print(c/a);
    };
    let a = (let b = 6 in b * 7) in print(a);
    print(let b = 6 in b * 7);
    let a = 20 in {
        let a = 42 in print(a);
        print(a);
    };
    let a = 7, a = 7 * 6 in print(a);
    let a = 7 in
        let a = 7 * 6 in
            print(a);
    let a = 0 in {
        print(a);
        a := 1;
        print(a);
    };
    let a = 0 in
        let b = a := 1 in {
            print(a);
            print(b);
        };
    let a = 42 in if (a % 2 == 0) print("Even") else print("odd");
    let a = 42 in print(if (a % 2 == 0) "even" else "odd");
    let a = 42 in
        if (a % 2 == 0) {
            print(a);
            print("Even");
        }
        else print("Odd");
    let a = 42, mod = a % 3 in 
        print(
            if (mod == 0) "Magic"
            elif (mod % 3 == 1) "Woke"
            else "Dumb"
        );
    let a = 10 in while (a >= 0) {
        print(a);
        a := a - 1;
    };
    
    for (x in range(0, 10)) print(x);
    let iterable = range(0, 10) in
        while (iterable.next())
            let x = iterable.current() in
                print(x);

    let pt = new Point() in 
        print("x: " @ pt.getX() @ "; y: " @ pt.getY());
    let pt = new Point(3,4) in
        print("x: " @ pt.getX() @ "; y: " @ pt.getY());
    let pt = new PolarPoint(3,4) in
        print("rho: " @ pt.rho());

    let p = new Knight("Phil", "Collins") in
        print(p.name());
        
    let p = new Person("Phil", "Collins") in
        print(p.name());
    let p: Person = new Knight("Phil", "Collins") in print(p.name());
    let x: Number = 42 in print(x);

    let p = new Person("Phil", "Collins") in
        let x: Number = fact(3)/print(p.name()) in print(x);
    
    
    let x = new Superman() in
        print(
            if (x is Bird) "It's bird!"
            elif (x is Plane) "It's a plane!"
            else "No, it's Superman!"
        );

    let x = 42 in print(x);
    let total = { print("Total"); 5; } + 6 in print(total);

    

    let x : A = if (rand() < 0.5) new B() else new C() in
        if (x is B)
            let y : B = x as B in {
                y.hello();
            }
        else {
            print("x cannot be downcasted to B");
        };

    let numbers = [1,2,3,4,5,6,7,8,9] in
        for (x in numbers)
            print(x);
    let numbers = [1,2,3,4,5,6,7,8,9] in print(numbers[7]);

    
    let squares = [x^2 || x in range(1,10)] in print(x);

    let squares = [x^2 || x in range(1,10)] in for (x in squares) print(x);
    let x : Hashable = new Person() in print(x.hash());
    let x : Hashable = new Point(0,0) in print(x.hash());

    let awacate: QueRico = new QueRico("siuuuu" @@ banda @ yaes + 4*5^2 @@ temporada_de_awacate == true) in aguacate.cascara("verde").lo_de_adentro(43*-1).semilla(true);
};
                '''

def print_error(message):
    red = "\033[31m"
    refresh = "\033[0m"
    print(f"{red}{message}{refresh}")

# def run_pipeline(input_path: Path, output_path: Path):
#     if not input_path.match('*.hulk'):
#         error = HulkIOError(HulkIOError.INVALID_EXTENSION % input_path)
#         print_error(error)
#         return

#     try:
#         with open(input_path) as f:
#             text = f.read()
#     except FileNotFoundError:
#         error = HulkIOError(HulkIOError.ERROR_READING_FILE % input_path)
#         print_error(error)
#         return

def run_pipeline(text):
    print('=================== TEXT ======================')
    print(text)
    print('================== TOKENS =====================')
    if os.path.isfile("lang/hulk_lexer.pkl"):
        lexer=load_object("lang/hulk_lexer.pkl")
    else:
        lexer=HulkLexer()
        save_object(lexer,"lang/hulk_lexer.pkl")
    tokens, lexicographic_errors = lexer(text)

    if lexicographic_errors:
        for err in lexicographic_errors:
            print_error(err)
        return
    
    print(tokens)
    print('=================== PARSE =====================')
    if os.path.isfile("lang/hulk_parser.pkl"):
        parser=load_object("lang/hulk_parser.pkl")
    else:
        parser = HulkParser()    
        save_object(parser,"lang/hulk_parser.pkl")
    derivations, operations, parsing_errors = parser(tokens)
    if parsing_errors:
        for err in parsing_errors:
            print_error(err)
        return
    # print('\n'.join(repr(x) for x in derivations))
    print('==================== AST ======================')
    ast = evaluate_reverse_parse(derivations, operations, tokens)
    formatter = FormatVisitor()
    tree = formatter.visit(ast)
    # print(tree)
    print('============== COLLECTING TYPES ===============')
    errors = []
    collector = TypeCollector(errors)
    collector.visit(ast)
    context = collector.context
    print('Errors:', errors)
    print('Context:')
    print(context)
    print('=============== BUILDING TYPES ================')
    builder = TypeBuilder(context, errors)
    builder.visit(ast)
    print('Errors: [')
    for error in errors:
        print('\t', error)
    print(']')
    print('Context:')
    print(context)
    print('=============== CHECKING TYPES ================')
    checker = TypeChecker(context, errors)
    scope = checker.visit(ast)
    print('Errors: [')
    for error in errors:
        print('\t', error)
    print(']')
    print('Context:')
    print(context)
    print('=============== HULK CONSOLE ================')
    if len(errors) == 0:
        interpreter = Interpreter(context, errors)
        value, type = interpreter.visit(ast)
        print(f'Value: {value} and Type: {type}')
    print('============================================')
    print('Errors: [')
    for error in errors:
        print('\t', error)
    print(']')
    print('Context:')
    print(context)
    return ast, errors, context, scope
    
if __name__ == "__main__":
    # inp = sys.argv[1]
    # input_path = Path(inp)
    # input_file_name = input_path.stem
    # output_file = Path(f'{input_file_name}.c')
    run_pipeline(text)
