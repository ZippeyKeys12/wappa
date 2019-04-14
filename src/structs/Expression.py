from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Tuple

if TYPE_CHECKING:
    from src.structs import Class


class Expression:
    def __init__(self, text):
        self.text = text

    def typeof(self):
        raise NotImplementedError("'typeof' not implemented")

    def compile(self, minify: bool = False) -> str:
        return self.text


class FunctionCallExpression(Expression):
    def __init__(self, ID: str, args: List[Expression],
                 kwargs: List[Tuple[str, Expression]], ret_type: Class):
        self.ID = ID
        self.args = args
        self.kwargs = kwargs
        self.ret_type = ret_type

    def compile(self, minify: bool = False) -> str:
        args = ""
        if self.args:
            args = ",".join([x.compile(minify) for x in self.args])

        kwargs = ""
        if self.kwargs:
            kwargs = ",".join(["{}:{}".format(x[0], x[1].compile(minify))
                               for x in self.kwargs])

            if self.args:
                kwargs = "," + kwargs

        return "{}({}{})".format(self.ID, args, kwargs)


class PostfixOPExpression(Expression):
    def __init__(self, expr, postfix):
        self.expr = expr
        self.postfix = postfix

    def typeof(self):
        return self.expr.typeof()

    def compile(self, minify: bool = False) -> str:
        uop = self.postfix

        if uop in ['++', '--']:
            return "({}{})".format(self.expr.compile(minify), uop)

        print("Fatal: Unhandled Postfix Operator {}".format(uop))
        return uop


class PrefixOPExpression(Expression):
    def __init__(self, prefix, expr):
        self.prefix = prefix
        self.expr = expr

    def compile(self, minify: bool = False) -> str:
        uop = self.prefix
        expr = self.expr.compile(minify)

        if uop in [
                '+', '++', '-', '--', '~', '!', 'alignof', 'sizeof']:
            return "({}{})".format(uop, expr)

        if uop == 'typeof':
            return "({}.getClassName())".format(expr)

        print("Fatal: Unhandled Prefix Operator {}".format(uop))
        return uop


class BinaryOPExpression(Expression):
    def __init__(self, exprL: Expression, bop, exprR: Expression):
        self.exprL = exprL
        self.bop = bop
        self.exprR = exprR

    def compile(self, minify: bool = False) -> str:
        data: Any
        bop = self.bop
        exprL = self.exprL.compile(minify)
        exprR = self.exprR.compile(minify)

        if bop in ['**', '*', '%', '+', '-', '<<', '>>', '>>>', '<=', '>=',
                   '<', '>', '&', '^', '|', '&&', '||', '=', '+=', '-=', '*=',
                   '&=', '|=', '^=', '<<=', '>>=', '>>>=', '%=']:
            data = (exprL, bop, exprR)
            if minify:
                return "({}{}{})".format(*data)

            return "({} {} {})".format(*data)

        converter = {
            '//': '/',
            '<=>': '<>=',
            '===': '==',
            '!==': '!=',
            '//=': '/='
        }
        if bop in converter.keys():
            data = (exprL, converter[bop], exprR)

            if minify:
                return "({}{}{})".format(*data)

            return "({} {} {})".format(*data)

        if bop == '/':
            return "({}/double({}))".format(exprL, exprR)

        if bop == 'is':
            return "{} is '{}'".format(exprL, exprR)

        if bop == '|>':
            return "({}({}))".format(exprR, exprL)

        if bop == '**=':
            data = (exprL, exprR)

            if minify:
                return "({0}={0}**{1})".format(*data)

            return "({0} = {0} ** {1})".format(*data)

        if bop == '/=':
            data = (exprL, exprR)

            if minify:
                return "({0}={0}/double({1}))".format(*data)

            return "({0} = {0} / double({1}))".format(*data)

        print("Fatal: Unhandled Binary Operator {}".format(bop))
        return bop


class TernaryOPExpression(Expression):
    def __init__(self, exprL: Expression, top: str,
                 exprC: Expression, exprR: Expression):
        self.exprL = exprL
        self.top = top
        self.exprC = exprC
        self.exprR = exprR

    def compile(self, minify: bool = False) -> str:
        top = self.top
        data = (self.exprL.compile(minify),
                self.exprC.compile(minify),
                self.exprR.compile(minify))

        if top == "?":
            if minify:
                return "({}?{}:{})".format(*data)

            return "({} ? {} : {})".format(*data)

        elif top == "<":
            if minify:
                return "({0}<{1}&&{1}<{2})".format(*data)

            return "({0} < {1} && {1} < {2})".format(*data)

        elif top == ">":
            if minify:
                return "({0}>{1}&&{1}>{2})".format(*data)

            return "({0} > {1} && {1} > {2})".format(*data)

        else:
            print("Error: Unhandled Ternary Operator {}".format(top))
            return top
