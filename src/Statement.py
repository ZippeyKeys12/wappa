from __future__ import annotations

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from src.Block import Block
    from src.Expression import Expression


class Statement:
    def __init__(self):
        pass

    def __call__(self) -> str:
        return ""


class IfStatement(Statement):
    def __init__(self, if_expr: Expression, if_block: Block = None,
                 elsif_exprs: List[Expression] = None,
                 elsif_blocks: List[Block] = None,
                 else_block: Block = None):
        self.if_expr = if_expr
        self.if_block = if_block
        self.elsif_exprs = elsif_exprs
        self.elsif_blocks = elsif_blocks
        self.else_block = else_block

    def __call__(self) -> str:
        ret = """
            if ({}) {}
        """.format(self.if_expr(), self.__compile_block(self.if_block))

        exprs = self.elsif_exprs
        blocks = self.elsif_blocks
        if exprs is not None and blocks is not None:
            for expr, block in zip(exprs, blocks):
                ret += """
                    else if ({}) {}
                """.format(expr, self.__compile_block(block))

        block = self.else_block
        if block is not None:
            ret += """
                else {}
            """.format(block())

        return ret

    def __compile_block(self, block):
        if block is not None:
            return block()
        else:
            return ""


class WhileStatement(Statement):
    def __init__(self, expr, block):
        self.expr = expr
        self.block = block

    def __call__(self):
        return """
            while ({}) {}
        """.format(self.expr(), self.block())


class UntilStatement(Statement):
    def __init__(self, expr, block):
        self.expr = expr
        self.block = block

    def __call__(self):
        return """
            until ({}) {}
        """.format(self.expr(), self.block())


class DoWhileStatement(Statement):
    def __init__(self, block, expr):
        self.block = block
        self.expr = expr

    def __call__(self):
        return "do {} while ({});".format(self.block(), self.expr())


class DoUntilStatement(Statement):
    def __init__(self, block, expr):
        self.block = block
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
