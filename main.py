import subprocess
import sys
from pathlib import Path

from cmp.errors import HulkIOError
from lexer.hulk_lexer import HulkLexer
from parser.evaluation import evaluate_reverse_parse
from parser.hulk_parser import HulkParser

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

    lexer = HulkLexer()
    parser = HulkParser()

    tokens, lexicographic_errors = lexer(text)

    if lexicographic_errors:
        for err in lexicographic_errors:
            print_error(err)
        return

    derivation, operations, syntactic_errors = parser(tokens)

    if syntactic_errors:
        for err in syntactic_errors:
            print_error(err)
        return
    
    ast = evaluate_reverse_parse(derivation, operations, tokens)


    # ast, semantic_errors, context, scope = semantic_analysis_pipeline(ast)

    # if semantic_errors:
    #     for err in semantic_errors:
    #         print_error(err)
    #     return

    # code_generator = CCodeGenerator()
    # code = code_generator(ast, context)

    # try:
    #     with open(output_path, 'w') as f:
    #         f.write(code)
    # except FileNotFoundError:
    #     error = HulkIOError(HulkIOError.ERROR_WRITING_FILE % output_path)
    #     print_error(error)
    #     return

    # subprocess.run(["gcc", output_file, "-o", "output.exe"], shell=True)
    # subprocess.run(['start', 'cmd', '/k', 'output.exe'], shell=True)





if __name__ == "__main__":
    inp = sys.argv[1]
    input_path = Path(inp)
    input_file_name = input_path.stem
    output_file = Path(f'{input_file_name}.c')
    run_pipeline(input_path, output_file)

