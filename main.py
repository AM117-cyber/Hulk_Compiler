import subprocess
import sys
from pathlib import Path

from cmp.errors import HulkIOError
from grammar.format_visitor import FormatVisitor
from grammar.hulk_grammar import G
from grammar.ast_nodes import UnaryNode, AtomicNode, BinaryNode
from lexer.hulk_lexer import HulkLexer
from parser.evaluation import evaluate_reverse_parse
from parser.hulk_parser import HulkParser
from cmp.ast import get_printer
from tests import customTest, testY, testX, test1, testZ, tests, test1
from semantic_checking.type_builder import TypeBuilder
from semantic_checking.type_collector import TypeCollector

# lexer = HulkLexer()
# parser = HulkParser()

# for i in range(2,7):
#     tokens = lexer(tests[i-2])
#     print(tokens)
#     parse, operations = parser([t.token_type for t in tokens])
#     ast = evaluate_reverse_parse(parse, operations, tokens)
#     formatter = FormatVisitor()
#     print(formatter.visit(ast))

# tokens, errors = lexer(test1)
# for t in tokens:
#     print(t)
# print(errors)
# print(tokens)
# parse, operations = parser([t.token_type for t in tokens])
# ast = evaluate_reverse_parse(parse, operations, tokens)
# formatter = FormatVisitor()
# print(formatter.visit(ast))

# print('EXITO')

text ='''
        protocol Serializable {
            serialize(): String;
        }

        type User(name: String, age: Number) {
            name = name;
            age = age;

            serialize(): String => "User(name: " @ self.name @ ", age: " @ self.age @ ")";
        }

        let user = new User("Alice", 30) in print(user.serialize());

                '''

def print_error(message):
    red = "\033[31m"
    refresh = "\033[0m"
    print(f"{red}{message}{refresh}")

def run_pipeline(input_path: Path, output_path: Path):
    if not input_path.match('*.hulk'):
        error = HulkIOError(HulkIOError.INVALID_EXTENSION % input_path)
        print_error(error)
        return

    try:
        with open(input_path) as f:
            text = f.read()
    except FileNotFoundError:
        error = HulkIOError(HulkIOError.ERROR_READING_FILE % input_path)
        print_error(error)
        return

    print('=================== TEXT ======================')
    print(text)
    print('================== TOKENS =====================')
    lexer = HulkLexer()
    tokens, lexicographic_errors = lexer(text)

    if lexicographic_errors:
        for err in lexicographic_errors:
            print_error(err)
        return
    
    print(tokens)
    print('=================== PARSE =====================')
    parser = HulkParser()
    derivations, operations, build_table_errors = parser([t.token_type for t in tokens])
    if build_table_errors:
        print_error("Grammar is not SLR(1)")
        for err in build_table_errors:
            print_error(f"There is a conflict at state {err.key}: current value is {err.prev_value} and tried to insert the new value {err.new_value}")
        return
    print('\n'.join(repr(x) for x in derivations))
    print('==================== AST ======================')
    ast = evaluate_reverse_parse(derivations, operations, tokens)
    formatter = FormatVisitor()
    tree = formatter.visit(ast)
    print(tree)
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
    return ast, errors, context
    
if __name__ == "__main__":
    inp = sys.argv[1]
    input_path = Path(inp)
    input_file_name = input_path.stem
    output_file = Path(f'{input_file_name}.c')
    run_pipeline(input_path, output_file)
