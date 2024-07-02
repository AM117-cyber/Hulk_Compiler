from colorama import Fore, Style

class HulkError(Exception):
    def __init__(self, text):
        super().__init__(text)

    @property
    def error_type(self):
        return 'HulkError'

    @property
    def text(self):
        return self.args[0]

    def __str__(self):
        return f'{self.error_type}: {self.text}'

    def __repr__(self):
        return str(self)
    
class HulkLexicographicError(HulkError):
    def __init__(self, text, line, column):
        super().__init__(text)
        self.line = line
        self.column = column

    def __str__(self):
        return f"{Fore.RED}{self.error_type}: {self.text} -> (line: {self.line}, column: {self.column}){Style.RESET_ALL}"

    UNKNOWN_TOKEN = 'Unknown token \'%s\'.'
    UNTERMINATED_STRING = 'Unterminated string \'%s\'.'

    @property
    def error_type(self):
        return 'LEXICOGRAPHIC ERROR'