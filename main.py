from antlr4 import CommonTokenStream, FileStream

from src import Wappa, WappaLexer, WappaMinifier, WappaVisitor


def main():
    input = FileStream("test.txt")
    lexer = WappaLexer(input)
    tokens = CommonTokenStream(lexer)
    parser = Wappa(tokens)
    parser.buildParseTrees = True

    minify = False
    tree = parser.compilationUnit()
    visitor = WappaVisitor(minify)
    text = visitor.visit(tree)

    if minify:
        minifier = WappaMinifier()
        text = minifier.zscript(text)

    with open("ex/zscript.txt", "w") as f:
        f.write(text)


if __name__ == "__main__":
    main()
