from io import TextIOWrapper
from typing import List, Optional, Tuple

from src.Class import Class
from src.Field import Field
from src.Function import Function
from src.gen.Wappa import Wappa
from src.gen.WappaVisitor import WappaVisitor as BaseVisitor


def Exception(arg, tok):
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

    def visitFunctionModifiers(self, ctx: Wappa.FunctionModifiersContext):
        return (
            # ctx.CONST() is not None,
            # ctx.OVERRIDE() is not None,
            self.__safe_text(ctx.visibilityModifier()),
            self.__safe_text(ctx.inheritanceModifier())
        )

    def visitFunctionDeclaration(self, ctx: Wappa.FunctionDeclarationContext):
        ID = ctx.IDENTIFIER()
        modifiers = self.visitFunctionModifiers(ctx.functionModifiers())
        parameters = self.visitParameterList(ctx.parameterList())
        ret_type = self.visitTypeOrVoid(ctx.typeOrVoid())
        stnts = self.visitBlock(ctx.block())

        return (ID, Function(ID, modifiers, parameters, ret_type, stnts))

    def visitParameterList(self, ctx: Wappa.ParameterListContext):
        if ctx is None:
            return None

        parameters: List[Tuple[str, str]] = []
        for ID, object_type in zip(ctx.IDENTIFIER(), ctx.typeOrVoid()):
            parameters.append((str(ID), self.visitTypeOrVoid(object_type)))

        return parameters

    def visitBlock(self, ctx: Wappa.BlockContext):
        return [self.visitStatement(x) for x in ctx.statement()]

    def visitStatement(self, ctx: Wappa.StatementContext):
        return ctx.getText()

    def visitTypeOrVoid(self, ctx: Wappa.TypeOrVoidContext):
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
