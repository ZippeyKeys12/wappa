from io import TextIOWrapper
from typing import Optional

from Class import Class
from Function import Function
from gen.Wappa import Wappa
from gen.WappaVisitor import WappaVisitor as BaseVisitor


class Exception:
    def __init__(self, arg, tok):
        print("{} at {}".format(arg, "Line {0.line}".format(tok)))
        exit()


class WappaVisitor(BaseVisitor):
    def __init__(self, file: TextIOWrapper):
        self.file = file
        self.classes = {}

        BaseVisitor.__init__(self)

    def visitCompilationUnit(self, ctx: Wappa.CompilationUnitContext):
        self.file.write('version "3.8"')

        ret = self.visitChildren(ctx)

        for ID, clazz in self.classes.items():
            self.file.write(clazz.compile(ID))

        return ret

    def visitClassDeclaration(self, ctx: Wappa.ClassDeclarationContext):
        ID = str(ctx.IDENTIFIER())

        if ID in self.classes:
            Exception('Conflicting declaration of "{}"'.format(ID), ctx.start)

        self.classes[ID] = Class(
            self.visitClassModifiers(ctx.classModifiers()))

        return self.visitChildren(ctx)

    def visitClassModifiers(self, ctx: Wappa.ClassModifiersContext):
        return (
            self.visitVisibilityModifier(ctx.visibilityModifier()),
            self.visitInheritanceModifier(ctx.inheritanceModifier())
        )

    def visitVisibilityModifier(self, ctx: Wappa.VisibilityModifierContext):
        return self.__safe_text(ctx)

    def visitInheritanceModifier(self, ctx: Wappa.InheritanceModifierContext):
        return self.__safe_text(ctx)

    def __safe_text(self, ctx) -> Optional[str]:
        if ctx is None:
            return None

        return ctx.getText()

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
