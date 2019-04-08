from __future__ import annotations

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from src.structs.Block import Block
    from src.structs.Expression import Expression


class Statement:
    def __init__(self, text: str = ""):
        self.text = text

    def __call__(self) -> str:
        return self.text


class IfStatement(Statement):
    def __init__(self, if_expr: Expression, if_block: Block,
                 elsif_exprs: List[Expression] = None,
                 elsif_blocks: List[Block] = None,
                 else_block: Block = None):
        self.if_expr = if_expr
        self.if_block, self.if_scope = if_block
        self.elsif_exprs = elsif_exprs
        self.elsif_blocks = elsif_blocks
        self.else_block = else_block

        if elsif_blocks is not None:
            self.elsif_blocks, self.elsif_scopes = elsif_blocks

        if else_block is not None:
            self.else_block, self.else_scope = else_block

    def __call__(self) -> str:
        ret = "if ({}) {}".format(self.if_expr(), self.if_block())

        exprs = self.elsif_exprs
        blocks = self.elsif_blocks
        if exprs is not None:
            for expr, block in zip(exprs, blocks):  # type: ignore
                ret += "else if ({}) {}".format(expr,
                                                block())

        block = self.else_block
        if block is not None:
            ret += "else {}".format(block())

        return ret


class WhileStatement(Statement):
    def __init__(self, expr, block):
        self.expr = expr
        self.block, self.scope = block

    def __call__(self):
        return "while ({}) {}".format(self.expr(), self.block())


class UntilStatement(Statement):
    def __init__(self, expr, block):
        self.expr = expr
        self.block, self.scope = block

    def __call__(self):
        return "until ({}) {}".format(self.expr(), self.block())


class DoWhileStatement(Statement):
    def __init__(self, block, expr):
        self.block, self.scope = block
        self.expr = expr

    def __call__(self):
        return "do {} while ({});".format(self.block(), self.expr())


class DoUntilStatement(Statement):
    def __init__(self, block, expr):
        self.block, self.scope = block
        self.expr = expr

    def __call__(self):
        return "do {} until ({});".format(self.block(), self.expr())


class ReturnStatement(Statement):
    def __init__(self, expr: Expression = None):
        self.expr = expr

    def __call__(self):
        expr = self.expr
        if expr is None:
            return "return;"
        else:
            return "return {};".format(expr())


class ExprStatement(Statement):
    def __init__(self, expr: Expression):
        self.expr = expr

    def __call__(self):
        return "{};".format(self.expr())
