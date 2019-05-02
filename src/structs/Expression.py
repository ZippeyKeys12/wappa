from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional, Tuple

from src.gen.Wappa import Token
from src.structs.Field import Field
from src.structs.Type import (BoolType, DoubleType, IntType, StringType,
                              TypeType, WappaType)
from src.structs.Variable import Variable
from src.util import Exception

if TYPE_CHECKING:
    from src.structs.Function import Function
    from src.structs.Scope import Symbol


class Expression:
    def __init__(self, tok: Token, text: str):
        self.tok = tok
        self.text = text

    def type_of(self) -> Optional[WappaType]:
        raise NotImplementedError(
            "'type_of' not implemented for {}".format(type(self)))

    def type_check(self):
        raise NotImplementedError(
            "'type_check' not implemented for {}".format(type(self)))

    def compile(self, minify: bool = False) -> str:
        return self.text


class Literal(Expression):
    def __init__(self, tok: Token, text: str, lit_type: WappaType):
        self.tok = tok
        self.text = text
        self.lit_type = lit_type

    def type_of(self) -> WappaType:
        return self.lit_type

    def type_check(self):
        pass

    def compile(self, minify: bool = False) -> str:
        return self.text


class Reference(Expression):
    def __init__(self, tok: Token, ref: Symbol):
        self.tok = tok
        self.ref = ref

    def type_of(self) -> Optional[WappaType]:
        if isinstance(self, WappaType):
            return self.ref

        if isinstance(self.ref, (Field, Variable)):
            return self.ref.type_of()

        return None

    def type_check(self):
        pass

    def compile(self, minify: bool = False) -> str:
        return self.ref.ID


class FunctionCallExpression(Expression):
    def __init__(self, tok: Token, ref: Function, args: List[Expression],
                 kwargs: List[Tuple[str, Expression]]):
        self.tok = tok
        self.ref = ref
        self.args = args
        self.kwargs = kwargs

    def type_of(self) -> Optional[WappaType]:
        return self.ref.ret_type

    def type_check(self):
        pass

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
    def __init__(self, tok: Token, expr, postfix):
        self.tok = tok
        self.expr = expr
        self.postfix = postfix

    def type_of(self) -> Optional[WappaType]:
        return self.expr.type_of()

    def compile(self, minify: bool = False) -> str:
        uop = self.postfix

        if uop in ['++', '--']:
            return "({}{})".format(self.expr.compile(minify), uop)

        Exception(
            "FATAL", "Unhandled Postfix Operator {}".format(uop), self.tok)
        return uop


class PrefixOPExpression(Expression):
    def __init__(self, tok: Token, prefix, expr):
        self.tok = tok
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

        Exception(
            "FATAL", "Unhandled Prefix Operator {}".format(uop), self.tok)

        return uop


class BinaryOPExpression(Expression):
    def __init__(self, tok: Token, exprL: Expression, bop, exprR: Expression):
        self.tok = tok
        self.exprL = exprL
        self.bop = bop
        self.exprR = exprR

    def type_of(self):
        bop = self.bop

        if bop in ['&&', '||',  '<=>', '==', '===', '!=', '!==', 'is']:
            return BoolType

        if bop in ['=', '+=', '-=', '*=', '**=', '/=', '//=', '&=', '|=', '^=',
                   '<<=', '>>=', '>>>=', '%=', '|>']:
            return self.exprR.type_of()

        if bop == '/':
            return DoubleType

        if bop == '//':
            return IntType

        return self.exprL.type_of()

    def compile(self, minify: bool = False) -> str:
        data: Any
        bop = self.bop
        exprL = self.exprL.compile(minify)
        exprR = self.exprR.compile(minify)

        if bop in ['**', '*', '%', '-', '<<', '>>', '>>>', '<=', '>=', '<',
                   '>', '&', '^', '|', '==', '!=', '&&', '||', '=', '+=', '-=',
                   '*=', '&=', '|=', '^=', '<<=', '>>=', '>>>=', '%=']:
            data = (exprL, bop, exprR)

            if minify:
                return "({}{}{})".format(*data)

            return "({} {} {})".format(*data)

        converter = {
            '<=>': '<>=',
            '===': '==',
            '!==': '!=',
            '~=': '~==',
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

        if bop == '//':
            return "floor({}/{})".format(exprL, exprR)

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

        Exception(
            "FATAL", "Unhandled Binary Operator {}".format(bop), self.tok)
        return bop


class TernaryOPExpression(Expression):
    def __init__(self, tok: Token, exprL: Expression, top: str,
                 exprC: Expression, exprR: Expression):
        self.tok = tok
        self.exprL = exprL
        self.top = top
        self.exprC = exprC
        self.exprR = exprR

    def type_of(self):
        top = self.top

        if top == '?':
            return self.exprC.type_of()

        if top in ['<', '>']:
            return BoolType

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
            Exception(
                "FATAL", "Unhandled Ternary Operator {}".format(top), self.tok)
            return top
