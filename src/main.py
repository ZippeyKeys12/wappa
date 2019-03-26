from antlr4 import CommonTokenStream, FileStream

from gen.Wappa import Wappa
from gen.WappaLexer import WappaLexer
from WappaVisitor import WappaVisitor


def main():
    input = FileStream("test.txt")
    lexer = WappaLexer(input)
    tokens = CommonTokenStream(lexer)
    parser = Wappa(tokens)
    parser.buildParseTrees = True

    tree = parser.compilationUnit()
    with open("output.txt", "w") as f:
        visitor = WappaVisitor(f)
        visitor.visit(tree)


if __name__ == "__main__":
    main()
