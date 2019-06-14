import llvmlite.binding as llvm
from antlr4 import CommonTokenStream, FileStream
from ctypes import CFUNCTYPE, c_double, c_int, c_bool

from compiler import Wappa, WappaLexer, WappaVisitor


def get_func(ee, name: str, *types):
    return CFUNCTYPE(*types)(  # pylint: disable=no-value-for-parameter
        ee.get_function_address(name))


def main(optimize: bool):
    text = FileStream("test.txt")
    lexer = WappaLexer(text)
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

    if optimize:
        builder = llvm.create_pass_manager_builder()
        builder.inlining_threshold = 2
        builder.loop_vectorize = True
        builder.opt_level = 3
        builder.slp_vectorize = True

        mpm = llvm.create_module_pass_manager()
        builder.populate(mpm)
        mpm.run(llvm_module)

    tm = llvm.Target.from_default_triple().create_target_machine()

    with llvm.create_mcjit_compiler(llvm_module, tm) as ee:
        ee.finalize_object()

        asm = tm.emit_assembly(llvm_module)

        # print('=== Assembly')
        # print(asm)

        with open('ex/test.asm', 'w') as f:
            f.write(asm)

        print('The result of "sum" is', get_func(
            ee, 'sum', c_double, c_int, c_int)(17, 42))

        print('The result of "eq" is', get_func(
            ee, 'eq', c_bool, c_double, c_double)(17, 42))

        print('The result of "neq" is', get_func(
            ee, 'neq', c_bool, c_double, c_double)(17, 42))


if __name__ == "__main__":
    main(True)
