import sys
from antlr4 import CommonTokenStream, InputStream
from gen.WappaLexer import WappaLexer
from gen.WappaParser import WappaParser


def main():
    input = InputStream(
        """
        x=1+1
    """
    )
    lexer = WappaLexer(input)
    stream = CommonTokenStream(lexer)
    parser = WappaParser(stream)
    tree = parser.compilationUnit()


if __name__ == "__main__":
    main()

