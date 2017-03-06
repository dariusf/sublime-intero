
import re

class HaskellError:
    def __init__(self, file, line, col, error):
        self.file = file
        self.line = line - 1
        self.col = col - 1
        self.error = error

    def __str__(self):
        return 'at {}:{}:{}: {}'.format(self.file, self.line, self.col, self.error)

def parse_header(header):
    header_segments = header.split(':')
    file = header_segments[0]
    line = int(header_segments[1])
    col = int(header_segments[2])
    return file, line, col

def parse_errors(errors):
    indent_size = re.search(r'\S', errors[0]).start()
    return '\n'.join([x[indent_size:] for x in errors])

def process(block):
    lines = block.rstrip().split('\n')

    header = lines[0]
    file, line, col = parse_header(header)

    rest = lines[1:]
    errors = parse_errors(rest)

    return HaskellError(file, line, col, errors)

# Looks for the first line with error location and selects the whole block.
# DOTALL makes . match newlines
intero_error = re.compile(r'[/\w]+\.hs:\d+:\d+:.*?(?=\n\n|Failed, modules)', re.DOTALL)

def parse(s):
    return [process(text) for text in intero_error.findall(s)]

# TODO move the cursor to the point and center it on error
# TODO cycle between errors?
# TODO clear all the indicators when stopping the plugin
# TODO clean up the output
# TODO pipe the output to a buffer?
