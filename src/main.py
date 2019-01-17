import sys

from antlr4 import CommonTokenStream, FileStream, ParseTreeWalker

from gen.Wappa import Wappa
from gen.WappaLexer import WappaLexer
from WappaVisitor import WappaVisitor


def main():
    input = FileStream("input.txt")
    lexer = WappaLexer(input)
    tokens = CommonTokenStream(lexer)
    parser = Wappa(tokens)
    parser.buildParseTrees = True

    tree = parser.compilationUnit()
    visitor = WappaVisitor()

    visitor.visit(tree)


if __name__ == "__main__":
    main()
