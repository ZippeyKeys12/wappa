from __future__ import annotations

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from src.structs.Block import Block
    from src.structs.Expression import Expression


class Statement:
    def __init__(self, text: str = ""):
        self.text = text

    def compile(self) -> str:
        return self.text


class IfStatement(Statement):
    def __init__(self, if_expr: Expression, if_block: Block,
                 elsif_exprs: List[Expression] = None,
                 elsif_blocks: List[Block] = None,
                 else_block: Block = None):
        self.if_expr = if_expr
        self.if_block = if_block
        self.elsif_exprs = elsif_exprs
        self.elsif_blocks = elsif_blocks
        self.else_block = else_block

    def compile(self) -> str:
        ret = "if ({}) {}".format(
            self.if_expr.compile(), self.if_block.compile())

        exprs = self.elsif_exprs
        blocks = self.elsif_blocks
        if exprs is not None:
            for expr, block in zip(exprs, blocks):  # type: ignore
                ret += "else if ({}) {}".format(expr.compile(),
                                                block.compile())

        block = self.else_block
        if block is not None:
            ret += "else {}".format(block.compile())

        return ret


class WhileStatement(Statement):
    def __init__(self, expr, block):
        self.expr = expr
        self.block = block

    def compile(self):
        return "while ({}) {}".format(
            self.expr.compile(), self.block.compile())


class UntilStatement(Statement):
    def __init__(self, expr, block):
        self.expr = expr
        self.block = block

    def compile(self):
        return "until ({}) {}".format(
            self.expr.compile(), self.block.compile())


class DoWhileStatement(Statement):
    def __init__(self, block, expr):
        self.block = block
        self.expr = expr

    def compile(self):
        return "do {} while ({});".format(
            self.block.compile(), self.expr.compile())


class DoUntilStatement(Statement):
    def __init__(self, block, expr):
        self.block = block
        self.expr = expr

    def compile(self):
        return "do {} until ({});".format(
            self.block.compile(), self.expr.compile())


class ReturnStatement(Statement):
    def __init__(self, expr: Expression = None):
        self.expr = expr

    def compile(self):
        expr = self.expr
        if expr is None:
            return "return;"
        else:
            return "return {};".format(expr.compile())


class ExprStatement(Statement):
    def __init__(self, expr: Expression):
        self.expr = expr

    def compile(self):
        return "{};".format(self.expr.compile())
