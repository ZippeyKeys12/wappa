from io import TextIOWrapper
from typing import List, Optional, Tuple

from src.gen.Wappa import Wappa
from src.gen.WappaVisitor import WappaVisitor as BaseVisitor
from src.structs import (BinaryOPExpression, Block, Class, DoUntilStatement,
                         DoWhileStatement, Expression, ExprStatement, Field,
                         Function, IfStatement, PostfixOPExpression,
                         PrefixOPExpression, ReturnStatement, Scope, Statement,
                         TernaryOPExpression, UntilStatement, Variable,
                         VariableDeclarationStatement, WhileStatement)


class WappaVisitor(BaseVisitor):
    def __init__(self, file: TextIOWrapper):
        self.file = file
        self.global_scope = Scope()
        self.scope = [self.global_scope]

        BaseVisitor.__init__(self)

    def visitCompilationUnit(self, ctx: Wappa.CompilationUnitContext):
        self.file.write('version "3.7.2"')

        ret = self.visitChildren(ctx)

        for _, clazz in self.global_scope.symbols():
            self.file.write(clazz.compile())

        return ret

    def visitClassDeclaration(self, ctx: Wappa.ClassDeclarationContext):
        ID = str(ctx.IDENTIFIER())

        parent = ctx.classParentDeclaration()

        if parent is not None:
            parent = self.visitClassParentDeclaration(parent)

        self.scope[-1].add_symbol(
            ctx.start, ID, Class(
                self.visitClassBlock(ctx.classBlock()), ID, parent,
                self.visitClassModifiers(ctx.classModifiers())))

    def visitClassModifiers(self, ctx: Wappa.ClassModifiersContext):
        return (
            self.__safe_text(ctx.visibilityModifier()),
            self.__safe_text(ctx.inheritanceModifier()),
            self.__safe_text(ctx.scopeModifier())
        )

    def visitClassParentDeclaration(self,
                                    ctx: Wappa.ClassParentDeclarationContext):
        return self.visitTypeName(ctx.typeName())

    def visitClassBlock(self, ctx: Wappa.ClassBlockContext):
        scope = Scope(parent=self.scope[-1])

        self.scope.append(scope)

        for member in ctx.memberDeclaration():
            self.visitChildren(member)

        self.scope.pop()

        return scope

    def visitFieldDeclaration(self, ctx: Wappa.FieldDeclarationContext):
        ID = ctx.variableDeclaratorId().getText()

        self.scope[-1].add_symbol(ctx.start, ID, Field(
            ID, ctx.typeName(), ctx.staticTypedVar(),
            (ctx.visibilityModifier(),),
            ctx.literal() or ctx.innerConstructorCall()))

    def visitFunctionModifiers(self, ctx: Wappa.FunctionModifiersContext
                               ) -> Optional[Tuple[
                                   bool, bool, Optional[str], Optional[str]]]:
        if ctx is None:
            return None

        return (ctx.immutable is not None, ctx.override is not None,
                self.__safe_text(ctx.visibilityModifier()),
                self.__safe_text(ctx.inheritanceModifier())
                )

    def visitFunctionDeclaration(self, ctx: Wappa.FunctionDeclarationContext):
        ID = ctx.IDENTIFIER().getText()
        modifiers = self.visitFunctionModifiers(ctx.functionModifiers())
        parameters = self.visitParameterList(ctx.parameterList())
        ret_type = self.visitTypeOrVoid(ctx.typeOrVoid())

        block = self.visitBlock(ctx.block())

        self.scope[-1].add_symbol(ctx.start, ID, Function(
            ID, modifiers, parameters, ret_type, block))

    def visitParameterList(self, ctx: Wappa.ParameterListContext
                           ) -> Optional[List[Tuple[str, Optional[str]]]]:
        if ctx is None:
            return None

        parameters: List[Tuple[str, Optional[str]]] = []
        for ID, object_type in zip(ctx.IDENTIFIER(), ctx.typeOrVoid()):
            parameters.append((str(ID), self.visitTypeOrVoid(object_type)))

        return parameters

    def visitVariableDeclaration(self, ctx: Wappa.VariableDeclarationContext):
        var_type = ctx.staticTypedVar().getText()

        if var_type == 'var':
            var_type = self.visitTypeName(ctx.typeName())
            name = self.visitVariableDeclaratorId(ctx.variableDeclaratorId())
            self.scope[-1].add_symbol(
                ctx.start, name, Variable(var_type, name))
            initializer = self.visitVariableInitializer(
                ctx.variableInitializer())

            return VariableDeclarationStatement(
                'var', var_type, name, initializer)

    def visitVariableDeclaratorId(
            self, ctx: Wappa.VariableDeclaratorIdContext):
        return ctx.IDENTIFIER()

    def visitVariableInitializer(self, ctx: Wappa.VariableInitializerContext
                                 ) -> Expression:
        return self.visitExpression(ctx.expression())

    def visitBlock(self, ctx: Wappa.BlockContext) -> Block:
        scope = Scope(parent=self.scope[-1])
        self.scope.append(scope)

        block = Block(scope, map(self.visitStatement, ctx.statement()))

        self.scope.pop()

        return block

    def visitStatement(self, ctx: Wappa.StatementContext) -> Statement:
        if ctx.getText() == ';':
            return Statement()

        if ctx.statementType is not None:
            statement_type = ctx.statementType.text
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

        if ctx.variableDeclarations():
            return self.visitVariableDeclarations(ctx.variableDeclarations())

        if ctx.expression(0):
            return ExprStatement(self.visitExpression(ctx.expression(0)))

    def visitExpression(self, ctx: Wappa.ExpressionContext):
        if ctx.postfix is not None:
            return PostfixOPExpression(
                self.visitExpression(ctx.expression(0)), ctx.postfix.text)

        if ctx.prefix is not None:
            return PrefixOPExpression(
                ctx.prefix.text, self.visitExpression(ctx.expression(0)))

        if ctx.bop is not None:
            return BinaryOPExpression(
                self.visitExpression(ctx.expression(0)),
                ctx.bop.text,
                self.visitExpression(ctx.expression(1)))

        if ctx.top is not None:
            return TernaryOPExpression(self.visitExpression(ctx.expression(0)),
                                       ctx.top.text,
                                       self.visitExpression(ctx.expression(1)),
                                       self.visitExpression(ctx.expression(2)))

        return Expression(ctx.getText())

    def visitIntegerLiteral(self, ctx: Wappa.IntegerLiteralContext) -> int:
        return int(ctx.text)

    def visitFloatLiteral(self, ctx: Wappa.FloatLiteralContext) -> float:
        return float(ctx.text)

    def visitTypeOrVoid(self, ctx: Wappa.TypeOrVoidContext) -> Optional[str]:
        if ctx is None:
            return None

        type_name = ctx.typeName()
        if type_name:
            return self.visitTypeName(type_name)

        return None

    def visitTypeName(self, ctx: Wappa.TypeNameContext):
        return self.scope[-1].get_symbol(ctx.start, ctx.getText())

    def __safe_text(self, ctx, func: str = "getText", default="") -> str:
        if ctx is None:
            return default

        ret = getattr(ctx, func)()
        if ret is not None:
            return ret

        return self.visitChildren(ctx)
