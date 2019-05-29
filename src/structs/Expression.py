from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Tuple

import llvmlite.ir as ir

from ..gen.Wappa import Token
from ..TypeSystem import BoolType, DoubleType, IntType, TypeType
from ..util import Exception
from .Field import Field
from .Type import WappaType
from .Variable import Variable

if TYPE_CHECKING:
    from .Function import Function
    from .Scope import Symbol
    from .Symbols import SymbolTable


class Expression:
    def __init__(self, tok: Token, text: str):
        self.tok = tok
        self.text = text

    def type_of(self) -> Optional[WappaType]:
        raise NotImplementedError(
            "'type_of' not implemented for {}".format(type(self)))

    def ir_type_of(self) -> Optional[ir.Value]:
        raise NotImplementedError(
            "'ir_type_of' not implemented for {}".format(type(self)))

    def type_check(self):
        raise NotImplementedError(
            "'type_check' not implemented for {}".format(type(self)))

    def compile(self, module: ir.Module, builder: ir.IRBuilder,
                symbols: SymbolTable) -> ir.Value:
        raise NotImplementedError(
            "'compile' not implemented for {}: {}".format(
                type(self), self.text))


class Literal(Expression):
    def __init__(self, tok: Token, text: str, lit_type: WappaType):
        self.tok = tok
        self.text = text
        self.lit_type = lit_type

    def type_of(self) -> WappaType:
        return self.lit_type

    def ir_type_of(self) -> ir.Value:
        return self.lit_type.ir_type

    def type_check(self):
        pass

    def compile(self, module: ir.Module, builder: ir.IRBuilder,
                symbols: SymbolTable) -> ir.Value:
        lit_type = self.lit_type

        if lit_type == IntType:
            return ir.Constant(lit_type.ir_type, int(self.text))

        if lit_type == DoubleType:
            return ir.Constant(lit_type.ir_type, float(self.text))

        if lit_type == BoolType:
            return ir.Constant(lit_type.ir_type, int(self.text == 'True'))


class Reference(Expression):
    def __init__(self, tok: Token, ref: Symbol, ID: str):
        self.tok = tok
        self.ref = ref
        self.ID = ID

    def type_of(self) -> Optional[WappaType]:
        if isinstance(self, WappaType):
            return self.ref

        if isinstance(self.ref, (Field, Variable)):
            return self.ref.type_of()

        return None

    def ir_type_of(self) -> Optional[ir.Value]:
        try:
            return self.type_of().ir_type
        except AttributeError:
            return None

    def type_check(self):
        pass

    def compile(self, module: ir.Module, builder: ir.IRBuilder,
                symbols: SymbolTable) -> ir.Value:
        return symbols.get_symbol(self.ID)


class FunctionCallExpression(Expression):
    def __init__(self, tok: Token, ref: Function, args: List[Expression],
                 kwargs: List[Tuple[str, Expression]]):
        self.tok = tok
        self.ref = ref
        self.args = args
        self.kwargs = kwargs

    def type_of(self) -> Optional[WappaType]:
        return self.ref.ret_type

    def ir_type_of(self) -> Optional[ir.Value]:
        try:
            return self.type_of().ir_type
        except AttributeError:
            return None

    def type_check(self):
        pass

    def compile(self, module: ir.Module, builder: ir.IRBuilder,
                symbols: SymbolTable) -> ir.Value:
        return builder.call(
            self.ref.compile(module, builder, symbols),
            [a.compile(module, builder, symbols) for a in self.args])


class PostfixOPExpression(Expression):
    def __init__(self, tok: Token, expr, postfix):
        self.tok = tok
        self.expr = expr
        self.postfix = postfix

    def type_of(self) -> Optional[WappaType]:
        return self.expr.type_of()

    def ir_type_of(self) -> Optional[ir.Value]:
        try:
            return self.type_of().ir_type
        except AttributeError:
            return None

    def compile(self, module: ir.Module, builder: ir.IRBuilder,
                symbols: SymbolTable) -> ir.Value:
        uop = self.postfix

        # TODO: Figure out postfix operators
        if uop in ['++', '--']:
            if self.expr.type_of() == IntType:
                pass

            if self.expr.type_of() == DoubleType:
                pass

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

    def ir_type_of(self) -> Optional[ir.Value]:
        try:
            return self.type_of().ir_type
        except AttributeError:
            return None

    def compile(self, module: ir.Module, builder: ir.IRBuilder,
                symbols: SymbolTable) -> ir.Value:
        uop = self.prefix
        expr = self.expr.compile(module, builder, symbols)

        if uop == '-':
            return builder.neg(expr)

        if uop in ['~', '!']:
            return builder.not_(expr)

        # if uop in ['+', '++', '-', '--', '~', '!', 'alignof', 'sizeof']:
        #     return "({}{})".format(uop, expr)

        # if uop == 'typeof':
        #     return "({}.getClassName())".format(expr)

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

    def ir_type_of(self) -> Optional[ir.Value]:
        try:
            return self.type_of().ir_type
        except AttributeError:
            return None

    def compile(self, module: ir.Module, builder: ir.IRBuilder,
                symbols: SymbolTable) -> ir.Value:
        bop = self.bop

        exprL = self.exprL.compile(module, builder, symbols)
        exprL_type = self.exprL.type_of()

        exprR = self.exprR.compile(module, builder, symbols)
        exprR_type = self.exprR.type_of()

        if bop == '+':
            if exprL_type == IntType and exprR_type == IntType:
                return builder.add(exprL, exprR)

            if exprL_type == IntType:
                exprL = builder.sitofp(exprL, DoubleType.ir_type)

            if exprR_type == IntType:
                exprR = builder.sitofp(exprR, DoubleType.ir_type)

            return builder.fadd(exprL, exprR)

        if bop == '-':
            if exprL_type == IntType and exprR_type == IntType:
                return builder.sub(exprL, exprR)

            if exprL_type == IntType:
                exprL = builder.sitofp(exprL, DoubleType.ir_type)

            if exprR_type == IntType:
                exprR = builder.sitofp(exprR, DoubleType.ir_type)

            return builder.fsub(exprL, exprR)

        if bop == '*':
            if exprL_type == IntType and exprR_type == IntType:
                return builder.mul(exprL, exprR)

            if exprL_type == IntType:
                exprL = builder.sitofp(exprL, DoubleType.ir_type)

            if exprR_type == IntType:
                exprR = builder.sitofp(exprR, DoubleType.ir_type)

            return builder.fmul(exprL, exprR)

        if bop == '/':
            if exprL_type == IntType:
                exprL = builder.sitofp(exprL, DoubleType.ir_type)

            if exprR_type == IntType:
                exprR = builder.sitofp(exprR, DoubleType.ir_type)

            return builder.fdiv(exprL, exprR)

        if bop == '//':
            return builder.sdiv(exprL, exprR)

        if bop == '%':
            if exprL_type == IntType and exprR_type == IntType:
                return builder.srem(exprL, exprR)

            if exprL_type == IntType:
                exprL = builder.sitofp(exprL, DoubleType.ir_type)

            if exprR_type == IntType:
                exprR = builder.sitofp(exprR, DoubleType.ir_type)

            return builder.frem(exprL, exprR)

        if bop in ['&', '&&']:
            return builder.and_(exprL, exprR)

        if bop in ['|', '||']:
            return builder.or_(exprL, exprR)

        if bop == '^':
            return builder.xor(exprL, exprR)

        if bop in ['<', '<=', '>=', '>']:
            if exprL_type == IntType and exprR_type == IntType:
                return builder.icmp_signed(bop, exprL, exprR)

            if exprL_type == IntType:
                exprL = builder.sitofp(exprL, DoubleType.ir_type)

            if exprR_type == IntType:
                exprR = builder.sitofp(exprR, DoubleType.ir_type)

            return builder.fcmp_ordered(bop, exprL, exprR)

        if bop == '==':
            if exprL_type == IntType and exprR_type == IntType:
                return builder.icmp_signed(bop, exprL, exprR)

            if exprL_type == IntType:
                exprL = builder.sitofp(exprL, DoubleType.ir_type)

            if exprR_type == IntType:
                exprR = builder.sitofp(exprR, DoubleType.ir_type)

            return builder.fcmp_ordered(bop, exprL, exprR)

        if bop == '!=':
            if exprL_type == IntType and exprR_type == IntType:
                return builder.icmp_signed(bop, exprL, exprR)

            if exprL_type == IntType:
                exprL = builder.sitofp(exprL, DoubleType.ir_type)

            if exprR_type == IntType:
                exprR = builder.sitofp(exprR, DoubleType.ir_type)

            return builder.fcmp_unordered(bop, exprL, exprR)

        # if bop == '**':

        # if bop in ['**', '*', '%', '-', '<<', '>>', '>>>', '<=', '>=', '<',
        #            '>', '&', '^', '|', '==', '!=', '&&', '||', '=', '+=',
        #            '-=', '*=', '&=', '|=', '^=', '<<=', '>>=', '>>>=', '%=']:
        #     data = (exprL, bop, exprR)

        #     if minify:
        #         return "({}{}{})".format(*data)

        #     return "({} {} {})".format(*data)

        # converter = {
        #     '<=>': '<>=',
        #     '===': '==',
        #     '!==': '!=',
        #     '~=': '~==',
        #     '//=': '/='
        # }
        # if bop in converter.keys():
        #     data = (exprL, converter[bop], exprR)

        #     if minify:
        #         return "({}{}{})".format(*data)

        #     return "({} {} {})".format(*data)

        # if bop == '+':
        #     if self.exprL.type_of() == StringType:
        #         return "{}..{}".format(exprL, exprR)

        #     return "{}+{}".format(exprL, exprR)

        # if bop == '/':
        #     return "({}/double({}))".format(exprL, exprR)

        # if bop == '//':
        #     return "floor({}/{})".format(exprL, exprR)

        # if bop == 'is':
        #     return "{} is '{}'".format(exprL, exprR)

        # if bop == '|>':
        #     return "({}({}))".format(exprR, exprL)

        # if bop == '**=':
        #     data = (exprL, exprR)

        #     if minify:
        #         return "({0}={0}**{1})".format(*data)

        #     return "({0} = {0} ** {1})".format(*data)

        # if bop == '/=':
        #     data = (exprL, exprR)

        #     if minify:
        #         return "({0}={0}/double({1}))".format(*data)

        #     return "({0} = {0} / double({1}))".format(*data)

        Exception(
            "FATAL", "Unhandled Binary Operator {}".format(bop), self.tok)
        return bop


class TernaryOPExpression(Expression):
    def __init__(self, tok: Token, exprL: Expression, exprC: Expression,
                 exprR: Expression):
        self.tok = tok

        self.exprL = exprL
        self.exprC = exprC
        self.exprR = exprR

    def type_of(self):
        return self.exprC.type_of()

    def ir_type_of(self) -> Optional[ir.Value]:
        try:
            return self.type_of().ir_type
        except AttributeError:
            return None

    def compile(self, module: ir.Module, builder: ir.IRBuilder,
                symbols: SymbolTable) -> ir.Value:
        data = (self.exprL.compile(module, builder, symbols),
                self.exprC.compile(module, builder, symbols),
                self.exprR.compile(module, builder, symbols))

        return builder.select(*data)
