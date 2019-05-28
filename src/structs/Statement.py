from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional

import llvmlite.ir as ir

from ..gen.Wappa import Token

if TYPE_CHECKING:
    from .Block import Block
    from .Expression import Expression
    from .Symbols import SymbolTable
    from .Type import WappaType


class Statement:
    def __init__(self, tok: Token, text: str = ""):
        self.tok = tok
        self.text = text

    def compile(self, module: ir.Module, builder: ir.IRBuilder,
                symbols: SymbolTable) -> ir.Value:
        return self.text


class IfStatement(Statement):
    def __init__(self, tok: Token, if_expr: Expression, if_block: Block,
                 elsif_exprs: List[Expression] = [],
                 elsif_blocks: List[Block] = [],
                 else_block: Optional[Block] = None):
        self.tok = tok
        self.if_expr = if_expr
        self.if_block = if_block
        self.elsif_exprs = elsif_exprs
        self.elsif_blocks = elsif_blocks
        self.else_block = else_block

    def compile(self, module: ir.Module, builder: ir.IRBuilder,
                symbols: SymbolTable) -> ir.Value:
        if len(self.elsif_exprs) == 0:
            if self.else_block:
                with builder.if_else(self.if_expr.compile(
                        module, builder, symbols)) as (then, otherwise):
                    with then:
                        self.if_block.compile(module, builder, symbols)

                    with otherwise:
                        self.else_block.compile(module, builder, symbols)

                    return
            else:
                with builder.if_then(
                        self.if_expr.compile(module, builder, symbols)):
                    self.if_block.compile(module, builder, symbols)

                return

        def build_elsif(elsifs):
            expr, block = elsifs
            with builder.if_else(expr.compile(
                    module, builder, symbols)) as (then, otherwise):
                with then:
                    block.compile(module, builder, symbols)

                with otherwise:
                    left = len(elsifs)
                    if left > 2:
                        build_elsif(elsifs[1:])

                    if left == 2:
                        expr, block = elsifs[1]

                        if self.else_block:
                            with builder.if_else(expr.compile(
                                    module, builder, symbols)) as (then,
                                                                   otherwise):
                                with then:
                                    block.compile(module, builder, symbols)

                                with otherwise:
                                    self.else_block.compile(
                                        module, builder, symbols)

                        else:
                            with builder.if_then(expr.compile(
                                    module, builder, symbols)):
                                block.compile(module, builder, symbols)

        with builder.if_else(self.if_expr.compile(
                module, builder, symbols)) as (then, otherwise):
            with then:
                self.if_block.compile(module, builder, symbols)

            with otherwise:
                build_elsif([(self.elsif_exprs[i], self.elsif_blocks[i])
                             for i in range(len(self.elsif_exprs))])

        # data: Any = (self.if_expr.compile(minify),
        #              self.if_block.compile(minify))

        # if minify:
        #     ret = "if({}){}".format(*data)
        # else:
        #     ret = "if ({}) {}".format(*data)

        # exprs = self.elsif_exprs
        # blocks = self.elsif_blocks
        # if exprs is not None and blocks is not None:
        #     for expr, block in zip(exprs, blocks):
        #         data = (expr.compile(minify), block.compile(minify))

        #         if minify:
        #             ret += "else if({}){}".format(*data)
        #         else:
        #             ret += "else if ({}) {}".format(*data)

        # if self.else_block is not None:
        #     data = self.else_block.compile(minify)

        #     if minify:
        #         ret += "else{}".format(data)

        #     else:
        #         ret += "else {}".format(data)

        # return ret


class WhileStatement(Statement):
    def __init__(self, tok: Token, expr, block):
        self.tok = tok
        self.expr = expr
        self.block = block

    def compile(self, module: ir.Module, builder: ir.IRBuilder,
                symbols: SymbolTable) -> ir.Value:
        return "while ({}) {}".format(
            self.expr.compile(minify), self.block.compile(minify))


class UntilStatement(Statement):
    def __init__(self, tok: Token, expr, block):
        self.tok = tok
        self.expr = expr
        self.block = block

    def compile(self, module: ir.Module, builder: ir.IRBuilder,
                symbols: SymbolTable) -> ir.Value:
        return "until ({}) {}".format(
            self.expr.compile(minify), self.block.compile(minify))


class DoWhileStatement(Statement):
    def __init__(self, tok: Token, block, expr):
        self.tok = tok
        self.block = block
        self.expr = expr

    def compile(self, module: ir.Module, builder: ir.IRBuilder,
                symbols: SymbolTable) -> ir.Value:
        return "do {} while ({});".format(
            self.block.compile(minify), self.expr.compile(minify))


class DoUntilStatement(Statement):
    def __init__(self, tok: Token, block, expr):
        self.tok = tok
        self.block = block
        self.expr = expr

    def compile(self, module: ir.Module, builder: ir.IRBuilder,
                symbols: SymbolTable) -> ir.Value:
        return "do {} until ({});".format(
            self.block.compile(minify), self.expr.compile(minify))


class ReturnStatement(Statement):
    def __init__(self, tok: Token, expr: Expression = None):
        self.tok = tok
        self.expr = expr

    def compile(self, module: ir.Module, builder: ir.IRBuilder,
                symbols: SymbolTable) -> ir.Value:
        expr = self.expr
        if expr is None:
            builder.ret_void()
        else:
            builder.ret(self.expr.compile(module, builder, symbols))


class VariableDeclarationStatement(Statement):
    def __init__(self, tok: Token, typed_var: str,
                 var_type: Optional[WappaType], ID: str,
                 initializer: Optional[Expression]):
        self.tok = tok
        self.typed_var = typed_var
        self.var_type = var_type
        self.ID = ID
        self.initializer = initializer

    def compile(self, module: ir.Module, builder: ir.IRBuilder,
                symbols: SymbolTable) -> ir.Value:
        var_type = 'let'
        if self.var_type:
            var_type = self.var_type.ID

        initializer: Any = self.initializer
        if initializer:
            initializer = "= {};".format(initializer.compile(minify))

        return "{} {} {}".format(var_type, self.ID, initializer or ";")


class VariableDeclarationsStatement(Statement):
    def __init__(self, tok: Token,
                 var_statements: List[VariableDeclarationStatement]):
        self.tok = tok
        self.var_statements = var_statements

    def compile(self, module: ir.Module, builder: ir.IRBuilder,
                symbols: SymbolTable) -> ir.Value:
        return "".join([x.compile(minify) for x in self.var_statements])


class ExprStatement(Statement):
    def __init__(self, tok: Token, expr: Expression):
        self.tok = tok
        self.expr = expr

    def compile(self, module: ir.Module, builder: ir.IRBuilder,
                symbols: SymbolTable) -> ir.Value:
        self.expr.compile(module, builder, symbols)
