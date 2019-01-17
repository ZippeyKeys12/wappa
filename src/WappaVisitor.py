from gen.Wappa import Wappa
from gen.WappaVisitor import WappaVisitor as BaseVisitor


class WappaVisitor(BaseVisitor):
    def _get_expression(self, ctx: Wappa.ExpressionContext, i: int = None):
        return self.visitExpression(ctx.expression(i))

    def visitExpression(self, ctx: Wappa.ExpressionContext):
        if ctx.primary():
            return self.visitPrimary(ctx.primary())

        if ctx.prefix:
            return self.visitChildren(ctx)

        if ctx.bop:
            bop = ctx.bop.text
            if bop == "?":
                if self._get_expression(ctx, 0):
                    return self._get_expression(ctx, 1)
                else:
                    return self._get_expression(ctx, 2)
            else:
                return {
                    "**": lambda a, b: a ** b,
                    "*": lambda a, b: a * b,
                    "/": lambda a, b: a / b,
                    "%": lambda a, b: a % b,
                    "+": lambda a, b: a + b,
                    "-": lambda a, b: a - b,
                    "<<": lambda a, b: a << b,
                    ">>": lambda a, b: a >> b,
                    "<=": lambda a, b: a <= b,
                    ">=": lambda a, b: a >= b,
                    ">": lambda a, b: a > b,
                    "<": lambda a, b: a < b,
                    "==": lambda a, b: a == b,
                    "!=": lambda a, b: a != b,
                    "&": lambda a, b: a & b,
                    "^": lambda a, b: a ^ b,
                    "|": lambda a, b: a | b,
                    "&&": lambda a, b: a and b,
                    "||": lambda a, b: a or b,
                }[bop](self._get_expression(ctx, 0), self._get_expression(ctx, 1))
            return self.visitChildren(ctx)

        if ctx.postfix:
            return self.visitChildren(ctx)

    def visitIntegerLiteral(self, ctx: Wappa.IntegerLiteralContext):
        return int(ctx.getText())

    def visitFloatLiteral(self, ctx: Wappa.FloatLiteralContext):
        return float(ctx.getText())
