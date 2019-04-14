from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    from src.structs import Class


class Expression:
    def __init__(self, text):
        self.text = text

    def typeof(self):
        raise NotImplementedError("'typeof' not implemented")

    def compile(self) -> str:
        return self.text


class FunctionCallExpression(Expression):
    def __init__(self, ID: str, args: List[Expression],
                 kwargs: List[Tuple[str, Expression]], ret_type: Class):
        self.ID = ID
        self.args = args
        self.kwargs = kwargs
        self.ret_type = ret_type

    def compile(self):
        args = ""
        if self.args:
            args = ",".join((x.compile() for x in self.args))

        kwargs = ""
        if self.kwargs:
            kwargs = ",".join(("{}:{}".format(x[0], x[1].compile())
                               for x in self.kwargs))

            if self.args:
                kwargs = "," + kwargs

        return "{}({}{})".format(self.ID, args, kwargs)


class PostfixOPExpression(Expression):
    def __init__(self, expr, postfix):
        self.expr = expr
        self.postfix = postfix

    def typeof(self):
        return self.expr.typeof()

    def compile(self):
        if self.postfix in ['++', '--']:
            return "({}{})".format(self.expr.compile(), self.postfix)


class PrefixOPExpression(Expression):
    def __init__(self, prefix, expr):
        self.prefix = prefix
        self.expr = expr

    def compile(self):
        expr = self.expr.compile()

        if self.prefix in [
                '+', '++', '-', '--', '~', '!', 'alignof', 'sizeof']:
            return "({}{})".format(self.prefix, expr)

        if self.prefix == 'typeof':
            return "({}.getClassName())".format(expr)


class BinaryOPExpression(Expression):
    def __init__(self, exprL: Expression, bop, exprR: Expression):
        self.exprL = exprL
        self.bop = bop
        self.exprR = exprR

    def compile(self) -> str:
        bop = self.bop
        exprL = self.exprL.compile()
        exprR = self.exprR.compile()

        if bop in ['**', '*', '%', '+', '-', '<<', '>>', '>>>', '<=', '>=',
                   '<', '>', '&', '^', '|', '&&', '||', '=', '+=', '-=', '*=',
                   '&=', '|=', '^=', '<<=', '>>=', '>>>=', '%=']:
            return "({} {} {})".format(exprL, bop, exprR)

        converter = {
            '//': '/',
            '<=>': '<>=',
            '===': '==',
            '!==': '!=',
            '//=': '/='
        }
        if bop in converter.keys():
            return "({} {} {})".format(exprL, converter[bop], exprR)

        if bop == '/':
            return "({}/double({}))".format(exprL, exprR)

        if bop == 'is':
            return "{} is '{}'".format(exprL, exprR)

        if bop == '|>':
            return "({} ({}))".format(exprR, exprL)

        if bop == '**=':
            return "({0} = {0} ** {1})".format(exprL, exprR)

        if bop == '/=':
            return "({0} = {0} / double({1}))".format(exprL, exprR)

        print("Fatal: Unhandled Binary Operator {}".format(bop))
        return bop


class TernaryOPExpression(Expression):
    def __init__(self, exprL: Expression, top: str,
                 exprC: Expression, exprR: Expression):
        self.exprL = exprL
        self.top = top
        self.exprC = exprC
        self.exprR = exprR

    def compile(self) -> str:
        top = self.top
        exprL = self.exprL.compile()
        exprC = self.exprC.compile()
        exprR = self.exprR.compile()

        if top == "?":
            return "({} ? {} : {})".format(exprL, exprC, exprR)

        elif top == "<":
            return "({0} < {1} && {1} < {2})".format(exprL, exprC, exprR)

        elif top == ">":
            return "({0} > {1} && {1} > {2})".format(exprL, exprC, exprR)

        else:
            print("Error: Unhandled Ternary Operator {}".format(top))
            return top
