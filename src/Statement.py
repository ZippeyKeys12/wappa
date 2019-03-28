from typing import List

from src.Expression import Expression


class Statement:
    def __init__(self):
        pass

    def __call__(self) -> str:
        return ""


class IfStatement(Statement):
    def __init__(self, ifExpr: Expression, ifBlock: List[Statement],
                 elsifExprs: List[Expression],
                 elsifBlocks: List[List[Statement]],
                 elseBlock: List[Statement]):
        self.ifExpr = ifExpr
        self.ifBlock = ifBlock
        self.elsifExprs = elsifExprs
        self.elsifBlocks = elsifBlocks
        self.elseBlock = elseBlock

    def __call__(self) -> str:
        return ""
