from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Any

if TYPE_CHECKING:
    from src.structs import Block, Class, Expression


class Statement:
    def __init__(self, text: str = ""):
        self.text = text

    def compile(self, minify: bool = False) -> str:
        return self.text


class IfStatement(Statement):
    def __init__(self, if_expr: Expression, if_block: Block,
                 elsif_exprs: List[Expression] = None,
                 elsif_blocks: List[Block] = None,
                 else_block: Optional[Block] = None):
        self.if_expr = if_expr
        self.if_block = if_block
        self.elsif_exprs = elsif_exprs
        self.elsif_blocks = elsif_blocks
        self.else_block = else_block

    def compile(self, minify: bool = False) -> str:
        ret = "if ({}) {}".format(
            self.if_expr.compile(minify), self.if_block.compile(minify))

        exprs = self.elsif_exprs
        blocks = self.elsif_blocks
        if exprs is not None and blocks is not None:
            for expr, block in zip(exprs, blocks):
                ret += "else if ({}) {}".format(expr.compile(minify),
                                                block.compile(minify))

        if self.else_block is not None:
            ret += "else {}".format(self.else_block.compile(minify))

        return ret


class WhileStatement(Statement):
    def __init__(self, expr, block):
        self.expr = expr
        self.block = block

    def compile(self, minify: bool = False) -> str:
        return "while ({}) {}".format(
            self.expr.compile(minify), self.block.compile(minify))


class UntilStatement(Statement):
    def __init__(self, expr, block):
        self.expr = expr
        self.block = block

    def compile(self, minify: bool = False) -> str:
        return "until ({}) {}".format(
            self.expr.compile(minify), self.block.compile(minify))


class DoWhileStatement(Statement):
    def __init__(self, block, expr):
        self.block = block
        self.expr = expr

    def compile(self, minify: bool = False) -> str:
        return "do {} while ({});".format(
            self.block.compile(minify), self.expr.compile(minify))


class DoUntilStatement(Statement):
    def __init__(self, block, expr):
        self.block = block
        self.expr = expr

    def compile(self, minify: bool = False) -> str:
        return "do {} until ({});".format(
            self.block.compile(minify), self.expr.compile(minify))


class ReturnStatement(Statement):
    def __init__(self, expr: Expression = None):
        self.expr = expr

    def compile(self, minify: bool = False) -> str:
        expr = self.expr
        if expr is None:
            return "return;"
        else:
            return "return {};".format(expr.compile(minify))


class VariableDeclarationStatement(Statement):
    def __init__(self, typed_var: str, var_type: Optional[Class], ID: str,
                 initializer: Optional[Expression]):
        self.typed_var = typed_var
        self.var_type = var_type
        self.ID = ID
        self.initializer = initializer

    def compile(self, minify: bool = False) -> str:
        var_type = 'let'
        if self.var_type:
            var_type = self.var_type.ID

        initializer: Any = self.initializer
        if initializer:
            initializer = "= {};".format(initializer.compile(minify))

        return "{} {} {}".format(var_type, self.ID, initializer or ";")


class VariableDeclarationsStatement(Statement):
    def __init__(self, var_statements: List[VariableDeclarationStatement]):
        self.var_statements = var_statements

    def compile(self, minify: bool = False) -> str:
        return "".join([x.compile(minify) for x in self.var_statements])


class ExprStatement(Statement):
    def __init__(self, expr: Expression):
        self.expr = expr

    def compile(self, minify: bool = False) -> str:
        return "{};".format(self.expr.compile(minify))
