from io import TextIOWrapper
from typing import Any, Dict, List, Optional, Tuple

from src.Block import Block
from src.Class import Class
from src.Expression import Expression, BinaryOPExpression, TernaryOPExpression
from src.Field import Field
from src.Function import Function
from src.gen.Wappa import Wappa
from src.gen.WappaVisitor import WappaVisitor as BaseVisitor
from src.Statement import (DoUntilStatement, DoWhileStatement, ExprStatement,
                           IfStatement, ReturnStatement, Statement,
                           UntilStatement, WhileStatement)


def Exception(arg, tok):
    print("{} at {}".format(arg, "Line {0.line}".format(tok)))
    exit()


class WappaVisitor(BaseVisitor):
    def __init__(self, file: TextIOWrapper):
        self.file = file
        self.classes: Dict[str, Class] = {}

        BaseVisitor.__init__(self)

    def visitCompilationUnit(self, ctx: Wappa.CompilationUnitContext):
        self.file.write('version "3.8"')

        ret = self.visitChildren(ctx)

        for _, clazz in self.classes.items():
            self.file.write(clazz())

        return ret

    def visitClassDeclaration(self, ctx: Wappa.ClassDeclarationContext):
        ID = str(ctx.IDENTIFIER())

        if ID in self.classes:
            Exception('Conflicting declaration of "{}"'.format(ID), ctx.start)

        parent = ctx.classParentDeclaration()

        if parent is not None:
            parent = self.visitClassParentDeclaration(parent)

        self.classes[ID] = Class(
            ID, parent, self.visitClassModifiers(ctx.classModifiers()))

        self.visitClassBlock(ctx.classBlock(), ID)

        # return self.classes[ID]

    def visitClassModifiers(self, ctx: Wappa.ClassModifiersContext):
        return (
            self.__safe_text(ctx.visibilityModifier()),
            self.__safe_text(ctx.inheritanceModifier())
        )

    def visitClassParentDeclaration(self,
                                    ctx: Wappa.ClassParentDeclarationContext):
        return self.__safe_text(ctx, "IDENTIFIER")

    def visitClassBlock(self, ctx: Wappa.ClassBlockContext, ID: str):
        for member in ctx.memberDeclaration():
            self.classes[ID].add_member(*self.visitChildren(member))

    def visitFieldDeclaration(self, ctx: Wappa.FieldDeclarationContext):
        ID = ctx.variableDeclaratorId()

        return (ID, Field(ID, ctx.typeName(), ctx.staticTypedVar(),
                          (ctx.visibilityModifier(),),
                          ctx.literal() or ctx.innerConstructorCall()))

    def visitFunctionModifiers(self, ctx: Wappa.FunctionModifiersContext
                               ) -> Optional[Tuple[
                                   bool, bool, Optional[str], Optional[str]]]:
        if ctx is None:
            return None

        return (
            ctx.immutable is not None,
            ctx.override is not None,
            self.__safe_text(ctx.visibilityModifier()),
            self.__safe_text(ctx.inheritanceModifier())
        )

    def visitFunctionDeclaration(self, ctx: Wappa.FunctionDeclarationContext
                                 ) -> Tuple[str, Function]:
        ID = ctx.IDENTIFIER()
        modifiers = self.visitFunctionModifiers(ctx.functionModifiers())
        parameters = self.visitParameterList(ctx.parameterList())
        ret_type = self.visitTypeOrVoid(ctx.typeOrVoid())
        block = self.visitBlock(ctx.block())

        return (ID, Function(ID, modifiers, parameters, ret_type, block))

    def visitParameterList(self, ctx: Wappa.ParameterListContext
                           ) -> Optional[List[Tuple[str, str]]]:
        if ctx is None:
            return None

        parameters: List[Tuple[str, str]] = []
        for ID, object_type in zip(ctx.IDENTIFIER(), ctx.typeOrVoid()):
            parameters.append((str(ID), self.visitTypeOrVoid(object_type)))

        return parameters

    def visitBlock(self, ctx: Wappa.BlockContext) -> Block:
        return Block(map(self.visitStatement, ctx.statement()))

    def visitStatement(self, ctx: Wappa.StatementContext) -> Statement:
        if ctx.getText() == ';':
            return Statement()

        statement_type: Any = ctx.statementType
        if statement_type is not None:
            statement_type = statement_type.text
            if statement_type == "if":
                exprs = ctx.expression()
                blocks = ctx.block()

                else_block = len(exprs) < len(blocks)

                elsif_exprs = elsif_blocks = None
                if len(exprs) > 1:
                    elsif_exprs = map(self.visitExpression, exprs[1:])
                    if else_block:
                        elsif_blocks = map(self.visitBlock, blocks[1:-1])
                    else:
                        elsif_blocks = map(self.visitBlock, blocks[1:])

                if else_block:
                    else_block = self.visitBlock(blocks[-1])

                return IfStatement(
                    self.visitExpression(exprs[0]),
                    self.visitBlock(blocks[0]),
                    elsif_exprs,
                    elsif_blocks,
                    else_block)

            elif statement_type == "while":
                return WhileStatement(self.visitExpression(ctx.expression(0)),
                                      self.visitBlock(ctx.block(0)))

            elif statement_type == "until":
                return UntilStatement(self.visitExpression(ctx.expression(0)),
                                      self.visitBlock(ctx.block(0)))

            elif statement_type == "do":
                block = self.visitBlock(ctx.block(0))
                expr = self.visitExpression(ctx.expression(0))
                if ctx.doType == "while":
                    return DoWhileStatement(block, expr)
                else:
                    return DoUntilStatement(block, expr)

            elif statement_type == "return":
                return ReturnStatement(self.visitExpression(ctx.expression(0)))

        return ExprStatement(self.visitExpression(ctx.expression(0)))

    def visitExpression(self, ctx: Wappa.ExpressionContext):
        if ctx.bop is not None:
            return BinaryOPExpression(
                self.visitExpression(ctx.expression(0)), ctx.bop.text,
                self.visitExpression(ctx.expression(1)))

        if ctx.top is not None:
            return TernaryOPExpression(self.visitExpression(ctx.expression(0)),
                                       self.visitExpression(ctx.expression(1)),
                                       self.visitExpression(ctx.expression(2)))

        return Expression(ctx.getText())

    def visitTypeOrVoid(self, ctx: Wappa.TypeOrVoidContext) -> str:
        if ctx is None:
            return "void"

        return self.__safe_text(ctx.typeName()) or "void"

    def __safe_text(self, ctx, func: str = "getText") -> Optional[str]:
        if ctx is None:
            return None

        ret = getattr(ctx, func)()
        if ret is not None:
            return ret

        return self.visitChildren(ctx)

    # def _get_expression(self, ctx: Wappa.ExpressionContext, i: int = None):
    #     return self.visitExpression(ctx.expression(i))

    # def visitExpression(self, ctx: Wappa.ExpressionContext):
    #     if ctx.primary():
    #         return self.visitPrimary(ctx.primary())

    #     if ctx.prefix:
    #         return self.visitChildren(ctx)

    #     if ctx.bop:
    #         bop = ctx.bop.text
    #         if bop == "?":
    #             if self._get_expression(ctx, 0):
    #                 return self._get_expression(ctx, 1)
    #             else:
    #                 return self._get_expression(ctx, 2)
    #         else:
    #             return {
    #                 "**": lambda a, b: a ** b,
    #                 "*": lambda a, b: a * b,
    #                 "/": lambda a, b: a / b,
    #                 "%": lambda a, b: a % b,
    #                 "+": lambda a, b: a + b,
    #                 "-": lambda a, b: a - b,
    #                 "<<": lambda a, b: a << b,
    #                 ">>": lambda a, b: a >> b,
    #                 "<=": lambda a, b: a <= b,
    #                 ">=": lambda a, b: a >= b,
    #                 ">": lambda a, b: a > b,
    #                 "<": lambda a, b: a < b,
    #                 "==": lambda a, b: a == b,
    #                 "!=": lambda a, b: a != b,
    #                 "&": lambda a, b: a & b,
    #                 "^": lambda a, b: a ^ b,
    #                 "|": lambda a, b: a | b,
    #                 "&&": lambda a, b: a and b,
    #                 "||": lambda a, b: a or b,
    #             }[bop](
    #                 self._get_expression(ctx, 0),
    #                 self._get_expression(ctx, 1)
    #             )
    #         return self.visitChildren(ctx)

    #     if ctx.postfix:
    #         return self.visitChildren(ctx)

    # def visitIntegerLiteral(self, ctx: Wappa.IntegerLiteralContext):
    #     return int(ctx.getText())

    # def visitFloatLiteral(self, ctx: Wappa.FloatLiteralContext):
    #     return float(ctx.getText())
