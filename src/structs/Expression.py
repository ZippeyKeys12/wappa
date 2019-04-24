from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional, Tuple

from src.structs.Field import Field
from src.structs.Type import (BooleanType, IntType, StringType, TypeType,
                              WappaType)
from src.structs.Variable import Variable

if TYPE_CHECKING:
    from src.structs.Function import Function
    from src.structs.Scope import Symbol


class Expression:
    def __init__(self, text):
        self.text = text

    def type_of(self) -> Optional[WappaType]:
        raise NotImplementedError(
            "'type_of' not implemented for {}".format(type(self)))

    def compile(self, minify: bool = False) -> str:
        return self.text


class Literal(Expression):
    def __init__(self, text: str, lit_type: WappaType):
        self.text = text
        self.lit_type = lit_type

    def type_of(self) -> Optional[WappaType]:
        return self.lit_type

    def compile(self, minify=False) -> str:
        return self.text


class Reference(Expression):
    def __init__(self, ref: Symbol):
        self.ref = ref

    def type_of(self) -> Optional[WappaType]:
        if isinstance(self, WappaType):
            return self.ref

        if isinstance(self, Variable):
            return self.ref.var_type

        if isinstance(self, Field):
            return self.ref.object_type

        return None

    def compile(self, minify=False) -> str:
        return self.ref.ID


class FunctionCallExpression(Expression):
    def __init__(self, ref: Function, args: List[Expression],
                 kwargs: List[Tuple[str, Expression]]):
        self.ref = ref
        self.args = args
        self.kwargs = kwargs

    def type_of(self) -> Optional[WappaType]:
        return self.ref.ret_type

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

        return "{}({}{})".format(self.ref.ID, args, kwargs)


class PostfixOPExpression(Expression):
    def __init__(self, expr, postfix):
        self.expr = expr
        self.postfix = postfix

    def type_of(self) -> Optional[WappaType]:
        return self.expr.type_of()

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

    def type_of(self):
        uop = self.prefix

        if uop in ['alignof', 'sizeof']:
            return IntType

        if uop == 'typeof':
            return TypeType(self.expr.type_of())

        return self.expr.type_of()

    def compile(self, minify: bool = False) -> str:
        uop = self.prefix
        expr = self.expr.compile(minify)

        if uop in ['+', '++', '-', '--', '~', '!', 'alignof', 'sizeof']:
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

    def type_of(self):
        bop = self.bop

        if bop in ['&&', '||',  '<=>', '==', '===', '!=', '!==', 'is']:
            return BooleanType

        if bop in ['=', '+=', '-=', '*=', '**=', '/=', '//=', '&=', '|=', '^=',
                   '<<=', '>>=', '>>>=', '%=', '|>']:
            return self.exprR.type_of()

        return self.exprL.type_of()

    def compile(self, minify: bool = False) -> str:
        data: Any
        bop = self.bop
        exprL = self.exprL.compile(minify)
        exprR = self.exprR.compile(minify)

        if bop in ['**', '*', '%', '-', '<<', '>>', '>>>', '<=', '>=', '<',
                   '>', '&', '^', '|', '&&', '||', '=', '+=', '-=', '*=', '&=',
                   '|=', '^=', '<<=', '>>=', '>>>=', '%=']:
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

        if bop == '+':
            if self.exprL.type_of() == StringType:
                return "{}..{}".format(exprL, exprR)

            return "{}+{}".format(exprL, exprR)

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

    def type_of(self):
        top = self.top

        if top == '?':
            return self.exprC.type_of()

        if top in ['<', '>']:
            return BooleanType

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
