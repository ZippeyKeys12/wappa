import llvmlite.binding as llvm
from antlr4 import CommonTokenStream, FileStream
from ctypes import CFUNCTYPE, c_double, c_int, c_bool

from src import Wappa, WappaLexer, WappaVisitor


def get_func(ee, name: str, *types):
    return CFUNCTYPE(*types)(  # pylint: disable=no-value-for-parameter
        ee.get_function_address(name))


def main():
    input = FileStream("test.txt")
    lexer = WappaLexer(input)
    tokens = CommonTokenStream(lexer)
    parser = Wappa(tokens)
    parser.buildParseTrees = True

    tree = parser.compilationUnit()
    visitor = WappaVisitor()
    module = visitor.visit(tree)

    with open("ex/test.ll", "w") as f:
        f.write(module)

    print('=== LLVM IR')
    print(module)

    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    llvm_module = llvm.parse_assembly(str(module))

    tm = llvm.Target.from_default_triple().create_target_machine()

    with llvm.create_mcjit_compiler(llvm_module, tm) as ee:
        ee.finalize_object()
        # print('=== Assembly')
        # print(tm.emit_assembly(llvm_module))

        with open('ex/test.asm', 'w') as f:
            f.write(tm.emit_assembly(llvm_module))

        res = get_func(ee, 'sum', c_double, c_int, c_int)(17, 42)

        print('The result of "sum" is', res)

        res = get_func(ee, 'eq', c_bool, c_double, c_double)(17, 42)

        print('The result of "eq" is', res)

        res = get_func(ee, 'neq', c_bool, c_double, c_double)(17, 42)

        print('The result of "neq" is', res)


if __name__ == "__main__":
    main()
