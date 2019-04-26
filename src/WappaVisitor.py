from typing import Any, List, Optional, Tuple

from src.gen.Wappa import Wappa
from src.gen.WappaVisitor import WappaVisitor as BaseVisitor
from src.stdlib import init_stdlib
from src.structs.Block import Block
from src.structs.Class import Class
from src.structs.Expression import (BinaryOPExpression, Expression,
                                    FunctionCallExpression, Literal,
                                    PostfixOPExpression, PrefixOPExpression,
                                    Reference, TernaryOPExpression)
from src.structs.Field import Field
from src.structs.Function import Function
from src.structs.Scope import Scope
from src.structs.Statement import (
    DoUntilStatement, DoWhileStatement, ExprStatement, IfStatement,
    ReturnStatement, Statement, UntilStatement, VariableDeclarationsStatement,
    VariableDeclarationStatement, WhileStatement)
from src.structs.Type import (BoolType, FloatType, IntType, NilType,
                              PrimitiveTypes, StringType, WappaType)
from src.structs.Variable import Variable


class WappaVisitor(BaseVisitor):
    def __init__(self, minify: bool = False):
        self.minify = minify

        self.ref_scope = Scope()
        self.global_scope = Scope(parent=self.ref_scope)
        self.scope = [self.global_scope]

        init_stdlib(self.ref_scope)

        BaseVisitor.__init__(self)

    def visit(self, tree):
        BaseVisitor.visit(self, tree)

        return 'version "3.7.2"\n{}'.format("".join([
            clazz.compile(self.minify) for clazz in self.global_scope.symbols(
                values=True)]))

    def visitCompilationUnit(self, ctx: Wappa.CompilationUnitContext):
        return self.visitChildren(ctx)

    def visitClassDeclaration(self, ctx: Wappa.ClassDeclarationContext):
        ID = str(ctx.IDENTIFIER())

        parent = ctx.classParentDeclaration()

        if parent is not None:
            parent = self.visitClassParentDeclaration(parent)

        scope = Scope(parent=self.scope[-1])

        self.scope[-1].add_symbol(ctx.start, ID, Class(
            scope, ID, parent, self.visitClassModifiers(ctx.classModifiers())))

        self.scope.append(scope)

        self.visitClassBlock(ctx.classBlock())

        self.scope.pop()

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

        for member in ctx.memberDeclaration():
            self.visitChildren(member)

    def visitFieldDeclaration(self, ctx: Wappa.FieldDeclarationContext):
        ID = ctx.variableDeclaratorId().getText()

        type_name = ctx.typeName()
        if type_name:
            type_name = self.visitTypeName(type_name)

        self.scope[-1].add_symbol(ctx.start, ID, Field(
            ID, type_name, ctx.staticTypedVar(),
            (ctx.visibilityModifier(),),
            ctx.literal() or ctx.innerConstructorCall()))

    def visitFunctionModifiers(self, ctx: Wappa.FunctionModifiersContext
                               ) -> Tuple[
                                   bool, bool, Optional[str], Optional[str]]:
        return (ctx.immutable is not None, ctx.override is not None,
                self.__safe_text(ctx.visibilityModifier()),
                self.__safe_text(ctx.inheritanceModifier())
                )

    def visitFunctionDeclaration(self, ctx: Wappa.FunctionDeclarationContext):
        ID = str(ctx.IDENTIFIER())
        modifiers = self.visitFunctionModifiers(ctx.functionModifiers())

        parameters: List[Tuple[str, WappaType]] = []
        if ctx.parameterList():
            parameters = self.visitParameterList(ctx.parameterList())

        ret_type = None
        if ctx.typeOrVoid():
            ret_type = self.visitTypeOrVoid(ctx.typeOrVoid())

        block = self.visitBlock(ctx.block())

        self.scope[-1].add_symbol(ctx.start, ID, Function(
            ID, modifiers, parameters, ret_type, block))

    def visitParameterList(self, ctx: Wappa.ParameterListContext
                           ) -> List[Tuple[str, WappaType]]:
        parameters: List[Tuple[str, WappaType]] = []
        for ID, object_type in zip(ctx.IDENTIFIER(), ctx.typeName()):
            parameters.append((str(ID), self.visitTypeName(object_type)))

        return parameters

    def visitFunctionCall(self, ctx: Wappa.FunctionCallContext) -> Expression:
        ID = str(ctx.IDENTIFIER())

        args: List[Expression] = []
        if ctx.expressionList():
            args = self.visitExpressionList(ctx.expressionList())

        kwargs: List[Tuple[str, Expression]] = []
        if ctx.functionKwarguments():
            kwargs = self.visitFunctionKwarguments(ctx.functionKwarguments())

        ref = self.scope[-1].get_symbol(ctx.start, ID)

        return FunctionCallExpression(ctx.start, ref, args, kwargs)

    def visitFunctionKwarguments(self, ctx: Wappa.FunctionKwargumentsContext
                                 ) -> List[Tuple[str, Expression]]:
        return [
            self.visitFunctionKwargument(k) for k in ctx.functionKwargument()]

    def visitFunctionKwargument(self, ctx: Wappa.FunctionKwargumentContext
                                ) -> Tuple[str, Expression]:
        return (str(ctx.IDENTIFIER()),
                self.visitExpression(ctx.expression()))

    def visitVariableDeclarations(
            self, ctx: Wappa.VariableDeclarationsContext):
        return VariableDeclarationsStatement(ctx.start, list(map(
            self.visitVariableDeclaration, ctx.variableDeclaration())))

    def visitVariableDeclaration(self, ctx: Wappa.VariableDeclarationContext):
        var_type = ctx.staticTypedVar().getText()

        if var_type == 'var':
            name = self.visitVariableDeclaratorId(ctx.variableDeclaratorId())

            initializer = self.visitVariableInitializer(
                ctx.variableInitializer())

            self.scope[-1].add_symbol(ctx.start, name,
                                      Variable(var_type, name))

            if ctx.typeName():
                var_type = self.visitTypeName(ctx.typeName())
            else:
                var_type = initializer.type_of()

            return VariableDeclarationStatement(
                ctx.start, 'var', var_type, name, initializer)

    def visitVariableDeclaratorId(
            self, ctx: Wappa.VariableDeclaratorIdContext) -> str:
        return str(ctx.IDENTIFIER())

    def visitVariableInitializer(self, ctx: Wappa.VariableInitializerContext
                                 ) -> Expression:
        return self.visitExpression(ctx.expression())

    def visitBlock(self, ctx: Wappa.BlockContext) -> Block:
        scope = Scope(parent=self.scope[-1])
        self.scope.append(scope)

        block = Block(scope, list(map(self.visitStatement, ctx.statement())))

        self.scope.pop()

        return block

    def visitStatement(self, ctx: Wappa.StatementContext) -> Statement:
        if ctx.getText() == ';':
            return Statement(ctx.start)

        if ctx.statementType is not None:
            statement_type = ctx.statementType.text
            if statement_type == "if":
                exprs = ctx.expression()
                blocks = ctx.block()

                else_block: Any = len(exprs) < len(blocks)

                elsif_exprs = elsif_blocks = None
                if len(exprs) > 1:
                    elsif_exprs = list(map(self.visitExpression, exprs[1:]))
                    if else_block:
                        elsif_blocks = list(map(self.visitBlock, blocks[1:-1]))
                    else:
                        elsif_blocks = list(map(self.visitBlock, blocks[1:]))

                if else_block:
                    else_block = self.visitBlock(blocks[-1])

                return IfStatement(
                    ctx.start,
                    self.visitExpression(exprs[0]),
                    self.visitBlock(blocks[0]),
                    elsif_exprs,
                    elsif_blocks,
                    else_block)

            elif statement_type == "while":
                return WhileStatement(ctx.start,
                                      self.visitExpression(ctx.expression(0)),
                                      self.visitBlock(ctx.block(0)))

            elif statement_type == "until":
                return UntilStatement(ctx.start,
                                      self.visitExpression(ctx.expression(0)),
                                      self.visitBlock(ctx.block(0)))

            elif statement_type == "do":
                block = self.visitBlock(ctx.block(0))
                expr = self.visitExpression(ctx.expression(0))
                if ctx.doType == "while":
                    return DoWhileStatement(ctx.start, block, expr)
                else:
                    return DoUntilStatement(ctx.start, block, expr)

            elif statement_type == "return":
                return ReturnStatement(
                    ctx.start, self.visitExpression(ctx.expression(0)))

        if ctx.variableDeclarations():
            return self.visitVariableDeclarations(ctx.variableDeclarations())

        if ctx.expression(0):
            return ExprStatement(
                ctx.start, self.visitExpression(ctx.expression(0)))

        print("Fatal: Unhandled Expression {}".format(ctx.getText()))
        return ctx

    def visitExpressionList(
            self, ctx: Wappa.ExpressionListContext) -> List[Expression]:
        return [self.visitExpression(e) for e in ctx.expression()]

    def visitExpression(self, ctx: Wappa.ExpressionContext) -> Expression:
        if ctx.primary():
            return self.visitPrimary(ctx.primary())

        if ctx.functionCall():
            return self.visitFunctionCall(ctx.functionCall())

        tok = ctx.start

        if ctx.postfix is not None:
            expr = self.visitExpression(ctx.expression(0))
            expr_type = expr.type_of()

            if expr_type is None:
                Exception("ERROR", "Expression has no type", tok)

            else:
                postfix = ctx.postfix.text

                if expr_type in PrimitiveTypes:
                    return PostfixOPExpression(tok, expr, postfix)

                ref = expr_type.get_member(tok, self.__magic_method({
                    '++': 'postinc',
                    '--': 'postdec'
                }[postfix]))

                if isinstance(ref, Function):
                    return FunctionCallExpression(tok, ref, [expr], [])

        if ctx.prefix is not None:
            expr = self.visitExpression(ctx.expression(0))
            expr_type = expr.type_of()

            if expr_type is None:
                Exception("ERROR", "Expression has no type", tok)

            else:
                prefix = ctx.prefix.text

                if (prefix in ['alignof', 'sizeof', 'typeof']
                        or expr_type in PrimitiveTypes):
                    return PrefixOPExpression(ctx.start, prefix, expr)

                ref = expr_type.get_member(tok, self.__magic_method({
                    '!': 'not',
                    '~': 'inv',
                    '+': 'pos',
                    '++': 'preinc',
                    '-': 'neg',
                    '--': 'predec'
                }[prefix]))

                if isinstance(ref, Function):
                    return FunctionCallExpression(tok, ref, [expr], [])

        if ctx.bop is not None:
            exprL = self.visitExpression(ctx.expression(0))
            exprR = self.visitExpression(ctx.expression(1))

            if expr_type is None:
                Exception("ERROR", "Expression has no type", tok)

            else:
                bop = ctx.bop.text

                return BinaryOPExpression(ctx.start, exprL, bop, exprR)

        if ctx.top is not None:
            return TernaryOPExpression(ctx.start,
                                       self.visitExpression(ctx.expression(0)),
                                       ctx.top.text,
                                       self.visitExpression(ctx.expression(1)),
                                       self.visitExpression(ctx.expression(2)))

        Exception("FATAL", "Unhandled Expression: {}".format(ctx.getText()),
                  ctx.start)
        exit(0)

    def visitPrimary(self, ctx: Wappa.PrimaryContext):
        if ctx.expression():
            return self.visitExpression(ctx.expression())

        ID = ctx.IDENTIFIER()
        if ID:
            return Reference(
                ctx.start, self.scope[-1].get_symbol(ctx.start, str(ID)))

        if ctx.literal():
            return self.visitLiteral(ctx.literal())

        return self.visitChildren(ctx)

    def visitLiteral(self, ctx: Wappa.LiteralContext) -> Literal:
        text = ctx.getText()

        if ctx.integerLiteral():
            return Literal(ctx.start, text, IntType)

        if ctx.floatLiteral():
            return Literal(ctx.start, text, FloatType)

        if ctx.STRING_LITERAL():
            return Literal(ctx.start, text, StringType)

        if ctx.BOOL_LITERAL():
            return Literal(ctx.start, text, BoolType)

        if ctx.NIL_LITERAL():
            return Literal(ctx.start, text, NilType)

        Exception("FATAL", "Unhandled Literal: {}".format(ctx.getText()),
                  ctx.start)
        exit(0)

    def visitTypeOrVoid(
            self, ctx: Wappa.TypeOrVoidContext) -> Optional[WappaType]:
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

    def __magic_method(self, ID: str):
        return "__{}__".format(ID)
