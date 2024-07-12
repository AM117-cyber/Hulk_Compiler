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
# from tests import customTest, testY, testX, test1, testZ, tests, test1
from semantic_checking.type_builder import TypeBuilder
from semantic_checking.type_collector import TypeCollector

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
    lexer = HulkLexer(use_cached=False)
    tokens, lexicographic_errors = lexer(text)

    if lexicographic_errors:
        for err in lexicographic_errors:
            print_error(err)
        return
    
    print(tokens)
    print('=================== PARSE =====================')
    parser = HulkParser(use_cached=False)
    derivations, operations, parsing_errors = parser(tokens)
    if parsing_errors:
        for err in parsing_errors:
            print_error(err)
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
    
run_pipeline(text)
# if __name__ == "__main__":
#     inp = sys.argv[1]
#     input_path = Path(inp)
#     input_file_name = input_path.stem
#     output_file = Path(f'{input_file_name}.c')
#     run_pipeline(input_path, output_file)
