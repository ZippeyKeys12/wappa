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
from src.structs.Type import (BoolType, DoubleType, IntType, NilType,
                              PrimitiveTypes, StringType, WappaType)
from src.structs.Variable import Variable
from src.util import Exception


class WappaVisitor(BaseVisitor):
    def __init__(self, minify: bool = False):
        self.minify = minify

        self.ref_scope = Scope()
        self.global_scope = Scope(parent=self.ref_scope)
        self.scope = [self.global_scope]

        self.ref_scope.add_symbol(None, "Bool", BoolType)
        self.ref_scope.add_symbol(None, "Int", IntType)
        self.ref_scope.add_symbol(None, "Double", DoubleType)
        self.ref_scope.add_symbol(None, "String", StringType)
        self.ref_scope.add_symbol(None, "Nil", NilType)

        init_stdlib(self.ref_scope)

        BaseVisitor.__init__(self)

    def visit(self, tree):
        BaseVisitor.visit(self, tree)

        return 'version "3.7.2"\n{}'.format("".join([
            clazz.compile(self.minify) for clazz in self.global_scope.symbols(
                values=True)]))

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
            ctx.start, ID, type_name, ctx.staticTypedVar(),
            (ctx.visibilityModifier(),),
            self.visitLiteral(ctx.literal())
            or self.visitInnerConstructorCall(ctx.innerConstructorCall())))

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

        scope = Scope(parent=self.scope[-1])
        self.scope.append(scope)

        for p in parameters:
            scope.add_symbol(ctx.start, p[0], p[1])

        block = self.visitBlock(ctx.block())

        self.scope.pop()

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

            init_type = initializer.type_of()
            if ctx.typeName():
                var_act_type = self.visitTypeName(ctx.typeName())
            else:
                var_act_type = init_type

            if init_type is not None:
                if not init_type.is_a(var_act_type):
                    Exception(
                        "ERROR",
                        "Expression of type {}, does not match type {}".format(
                            init_type.ID, var_act_type.ID), ctx.start)

            self.scope[-1].add_symbol(ctx.start, name,
                                      Variable(name, var_act_type))

            return VariableDeclarationStatement(
                ctx.start, var_type, var_act_type, name, initializer)

        # TODO: if var_type == 'val':

    def visitVariableDeclaratorId(
            self, ctx: Wappa.VariableDeclaratorIdContext) -> str:
        return str(ctx.IDENTIFIER())

    def visitVariableInitializer(self, ctx: Wappa.VariableInitializerContext
                                 ) -> Expression:
        return self.visitExpression(ctx.expression())

    def visitBlock(self, ctx: Wappa.BlockContext) -> Block:
        block = Block(
            self.scope[-1], list(map(self.visitStatement, ctx.statement())))

        return block

    def visitStatement(self, ctx: Wappa.StatementContext) -> Statement:
        if ctx.getText() == ';':
            return Statement(ctx.start)

        if ctx.statementType is not None:
            statement_type = ctx.statementType.text
            if statement_type == "if":
                exprs = ctx.expression()
                blocks = ctx.block()

                scope = Scope(parent=self.scope[-1])
                self.scope.append(scope)

                block = self.visitBlock(blocks[0])

                self.scope.pop()

                else_block: Any = len(exprs) < len(blocks)

                elsif_exprs = elsif_blocks = None
                if len(exprs) > 1:
                    elsif_exprs = list(map(self.visitExpression, exprs[1:]))
                    if else_block:
                        elsif_blocks = []
                        for b in blocks[1:-1]:
                            scope = Scope(parent=self.scope[-1])
                            self.scope.append(scope)

                            elsif_blocks.append(self.visitBlock(b))

                            self.scope.pop()
                    else:
                        elsif_blocks = []
                        for b in blocks[1:]:
                            scope = Scope(parent=self.scope[-1])
                            self.scope.append(scope)

                            elsif_blocks.append(self.visitBlock(b))

                            self.scope.pop()

                if else_block:
                    scope = Scope(parent=self.scope[-1])
                    self.scope.append(scope)

                    else_block = self.visitBlock(blocks[-1])

                    self.scope.pop()

                return IfStatement(
                    ctx.start,
                    self.visitExpression(exprs[0]),
                    block,
                    elsif_exprs,
                    elsif_blocks,
                    else_block)

            elif statement_type == "while":
                scope = Scope(parent=self.scope[-1])
                self.scope.append(scope)

                block = self.visitBlock(ctx.block(0))

                self.scope.pop()

                return WhileStatement(
                    ctx.start, self.visitExpression(ctx.expression(0)), block)

            elif statement_type == "until":
                scope = Scope(parent=self.scope[-1])
                self.scope.append(scope)

                block = self.visitBlock(ctx.block(0))

                self.scope.pop()

                return UntilStatement(
                    ctx.start, self.visitExpression(ctx.expression(0)), block)

            elif statement_type == "do":
                scope = Scope(parent=self.scope[-1])
                self.scope.append(scope)

                block = self.visitBlock(ctx.block(0))

                self.scope.pop()

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

        Exception("FATAL", "Unhandled Expression {}".format(
            ctx.getText()), ctx.start)
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

                func_name = self.__magic_method({
                    '++': 'postinc',
                    '--': 'postdec'
                }[postfix])

                ref = expr_type.get_member(tok, func_name)

                if ref is None:
                    return Expression(tok, "ERROR")

                if isinstance(ref, Function):
                    return FunctionCallExpression(tok, ref, [], [])

                Exception(
                    "ERROR", "{} is not a function".format(func_name), tok)

                return Expression(tok, "ERROR")

        if ctx.prefix is not None:
            expr = self.visitExpression(ctx.expression(0))
            expr_type = expr.type_of()

            if expr_type is None:
                Exception("ERROR", "Expression has no type", tok)

                return Expression(tok, "ERROR")

            else:
                prefix = ctx.prefix.text

                if (prefix in ['alignof', 'sizeof', 'typeof']
                        or expr_type in PrimitiveTypes):
                    return PrefixOPExpression(ctx.start, prefix, expr)

                func_name = self.__magic_method({
                    '!': 'not',
                    '~': 'inv',
                    '+': 'pos',
                    '++': 'preinc',
                    '-': 'neg',
                    '--': 'predec'
                }[prefix])

                ref = expr_type.get_member(tok, func_name)

                if ref is None:
                    return Expression(tok, "ERROR")

                if isinstance(ref, Function):
                    return FunctionCallExpression(tok, ref, [], [])

                Exception(
                    "ERROR", "{} is not a function".format(func_name), tok)

                return Expression(tok, "ERROR")

        if ctx.bop is not None:
            exprL = self.visitExpression(ctx.expression(0))
            exprR = self.visitExpression(ctx.expression(1))
            expr_type = exprL.type_of()

            if expr_type is None:
                Exception("ERROR", "Expression has no type", tok)

                return Expression(tok, "ERROR")

            else:
                bop = ctx.bop.text

                if (bop in ['&&', '||', '===', '!==', 'is', ]
                        or expr_type in PrimitiveTypes):
                    return BinaryOPExpression(tok, exprL, bop, exprR)

                func_name = self.__magic_method({
                    '+': 'add',
                    '-': 'sub',
                    '*': 'mul',
                    '**': 'pow',
                    '/': 'div',
                    '//': 'ddiv',
                    '%': 'mod',
                    '<': 'lt',
                    '<<': 'lshift',
                    '>': 'gt',
                    '>>': 'rshift',
                    '>>>': 'urshift',
                    '&': 'and',
                    '|': 'or',
                    '^': 'xor',
                    '<=': 'le',
                    '>=': 'ge',
                    '==': 'eq',
                    '~=': 'aeq',
                    '!=': 'ne'
                }[bop])

                # TODO: Infer comparison operators
                # TODO: Implement assignment operators
                # a+=b -> a=a.__add__(b)
                ref = expr_type.get_member(tok, func_name)

                if ref is None:
                    return Expression(tok, "ERROR")

                if isinstance(ref, Function):
                    return FunctionCallExpression(tok, ref, [exprR], [])

                Exception(
                    "ERROR", "{} is not a function".format(func_name), tok)

                return Expression(tok, "ERROR")

        if ctx.top is not None:
            exprL = self.visitExpression(ctx.expression(0))
            exprC = self.visitExpression(ctx.expression(1))
            exprR = self.visitExpression(ctx.expression(2))
            expr_type = exprC.type_of()

            if expr_type is None:
                Exception("ERROR", "Expression has no type", tok)

                return Expression(tok, "ERROR")

            else:
                top = ctx.top.text

                if top == '?' or expr_type in PrimitiveTypes:
                    return TernaryOPExpression(tok, exprL, top, exprC, exprR)

                if top in ['<', '>']:
                    top = {
                        '<': 'lt',
                        '>': 'gt'
                    }[top]
                    func_nameL = self.__magic_method(
                        {'lt': 'gt', 'gt': 'lt'}[top])
                    func_nameR = self.__magic_method(top)

                    refL = expr_type.get_member(tok, func_nameL)
                    refR = expr_type.get_member(tok, func_nameR)

                    if refL or refR is None:
                        return Expression(tok, "ERROR")

                    if (isinstance(refL, Function)
                            and isinstance(refR, Function)):
                        exprL = FunctionCallExpression(tok, refL, [exprL], [])
                        exprR = FunctionCallExpression(tok, refR, [exprR], [])
                        return BinaryOPExpression(tok, exprL, '&&', exprR)

                    if refL is not None and not isinstance(refL, Function):
                        Exception(
                            "ERROR", "{} is not a function".format(func_nameL),
                            tok)

                    if refR is not None and not isinstance(refR, Function):
                        Exception(
                            "ERROR", "{} is not a function".format(func_nameR),
                            tok)

                    return Expression(tok, "ERROR")

        Exception("FATAL", "Unhandled Expression: {}".format(
            ctx.getText()), tok)

        return Expression(tok, "FATAL")

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
            return Literal(ctx.start, text, DoubleType)

        if ctx.STRING_LITERAL():
            return Literal(ctx.start, text, StringType)

        if ctx.BOOL_LITERAL():
            return Literal(ctx.start, text, BoolType)

        if ctx.NIL_LITERAL():
            return Literal(ctx.start, text, NilType)

        Exception("FATAL", "Unhandled Literal: {}".format(ctx.getText()),
                  ctx.start)

        return Literal(ctx.start, text, NilType)

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
