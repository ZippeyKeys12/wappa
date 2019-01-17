import sys

from antlr4 import CommonTokenStream, FileStream, ParseTreeWalker

from gen.Wappa import Wappa
from gen.WappaLexer import WappaLexer
from WappaListener import WappaListener


def main():
    input = FileStream("input.txt")
    lexer = WappaLexer(input)
    tokens = CommonTokenStream(lexer)
    parser = Wappa(tokens)
    tree = parser.compilationUnit()
    listener = WappaListener()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)


if __name__ == "__main__":
    main()
