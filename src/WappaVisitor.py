from typing import Any, List, Optional, Tuple

import llvmlite.ir as ir

from src.gen.Wappa import Wappa
from src.gen.WappaVisitor import WappaVisitor as BaseVisitor
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
from src.structs.Symbols import SymbolTable
from src.structs.Type import WappaType
from src.structs.Variable import Variable
from src.TypeSystem import (
    BoolType, DoubleType, IntType, NilType, ObjectType, PrimitiveTypes,
    StringType, TypeSolver, UnitType)
from src.util import EXCEPTION_LIST, Exception


class WappaVisitor(BaseVisitor):
    def __init__(self):
        self.ref_scope = Scope()
        self.global_scope = Scope(parent=self.ref_scope)
        self.scope = [self.global_scope]

        self.ref_scope.add_symbol(None, "Bool", BoolType)
        self.ref_scope.add_symbol(None, "Int", IntType)
        self.ref_scope.add_symbol(None, "Double", DoubleType)
        self.ref_scope.add_symbol(None, "Str", StringType)
        self.ref_scope.add_symbol(None, "Nil", NilType)
        self.ref_scope.add_symbol(None, "Unit", UnitType)

        BaseVisitor.__init__(self)

        self.module = ir.Module()

        self.builder = ir.IRBuilder()

        self.tsolver = TypeSolver()

    def visit(self, tree) -> str:
        BaseVisitor.visit(self, tree)

        for obj in self.global_scope.symbols(values=True):
            if hasattr(obj, 'compile'):
                obj.compile(self.module, self.builder, SymbolTable())

        for exception in sorted(set(EXCEPTION_LIST), key=lambda x: x[3]):
            print("{}[{}] - {} at line {}{}".format(*exception))

        return str(self.module)

    def visitClassDeclaration(
            self, ctx: Wappa.ClassDeclarationContext) -> None:
        ID = str(ctx.IDENTIFIER())

        parent = ctx.classParentDeclaration()

        if parent is not None:
            parent = self.visitClassParentDeclaration(parent)
        else:
            parent = ObjectType

        scope = Scope(parent=self.scope[-1])

        self.scope[-1].add_symbol(ctx.start, ID, Class(
            scope, ID, parent, self.visitClassModifiers(ctx.classModifiers())))

        self.scope.append(scope)

        self.visitClassBlock(ctx.classBlock())

        self.scope.pop()

    def visitClassModifiers(
            self, ctx: Wappa.ClassModifiersContext) -> Tuple[str, str, str]:
        return (
            self.__safe_text(ctx.visibilityModifier()),
            self.__safe_text(ctx.inheritanceModifier()),
            self.__safe_text(ctx.scopeModifier())
        )

    def visitClassParentDeclaration(
            self, ctx: Wappa.ClassParentDeclarationContext
    ) -> Optional[WappaType]:
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
        if ctx.typeOrUnit():
            ret_type = self.visitTypeOrUnit(ctx.typeOrUnit())

        scope = Scope(parent=self.scope[-1])
        self.scope.append(scope)

        tok = ctx.start

        for p in parameters:
            ID = p[0]
            scope.add_symbol(tok, ID, Variable(ID, p[1]))

        if ctx.expression():
            expr = ctx.expression()

            if ret_type and ret_type != UnitType:
                stmt = ReturnStatement(
                    expr.start, self.visitExpression(expr))
            else:
                stmt = ExprStatement(
                    expr.start, self.visitExpression(expr))

            block = Block(
                self.scope[-1], [stmt])
        else:
            block = self.visitBlock(ctx.block())

        self.scope.pop()

        ID = str(ctx.IDENTIFIER())
        self.scope[-1].add_symbol(ctx.start, ID, Function(
            ID, modifiers, parameters, ret_type, block))

    def visitMethodDeclaration(self, ctx: Wappa.MethodDeclarationContext):
        modifiers = self.visitFunctionModifiers(ctx.functionModifiers())

        parameters: List[Tuple[str, WappaType]] = []
        if ctx.parameterList():
            parameters = self.visitParameterList(ctx.parameterList())

        ret_type = None
        if ctx.typeOrUnit():
            ret_type = self.visitTypeOrUnit(ctx.typeOrUnit())

        scope = Scope(parent=self.scope[-1])
        self.scope.append(scope)

        tok = ctx.start

        ref = ctx.ref
        if ref.text == 'self':
            scope.add_symbol(ref.start, 'self', Variable(
                'self', scope.parent.owner))

        for p in parameters:
            ID = p[0]
            scope.add_symbol(tok, ID, Variable(ID, p[1]))

        if ctx.expression():
            expr = ctx.expression()

            if ret_type and ret_type != UnitType:
                stmt = ReturnStatement(
                    expr.start, self.visitExpression(expr))
            else:
                stmt = ExprStatement(
                    expr.start, self.visitExpression(expr))

            block = Block(
                self.scope[-1], [stmt])
        else:
            block = self.visitBlock(ctx.block())

        self.scope.pop()

        ID = str(ctx.IDENTIFIER())
        self.scope[-1].add_symbol(tok, ID, Function(
            ID, modifiers, parameters, ret_type, block))

    def visitParameterList(self, ctx: Wappa.ParameterListContext
                           ) -> List[Tuple[str, WappaType]]:
        parameters: List[Tuple[str, WappaType]] = []
        for ID, object_type in zip(ctx.IDENTIFIER(), ctx.typeExpression()):
            parameters.append((str(ID), self.visitTypeExpression(object_type)))

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
                if not init_type.is_a(self.tsolver, var_act_type):
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

                elsif_exprs = elsif_blocks = []
                if len(exprs) > 1:
                    elsif_exprs = list(map(self.visitExpression, exprs[1:]))
                    if else_block:
                        for b in blocks[1:-1]:
                            scope = Scope(parent=self.scope[-1])
                            self.scope.append(scope)

                            elsif_blocks.append(self.visitBlock(b))

                            self.scope.pop()
                    else:
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

            if (hasattr(expr, "text") and expr.text == "ERROR"):
                return Expression(tok, "ERROR")

            if isinstance(expr, Reference) and not expr.ref:
                Exception(
                    'ERROR', "Unknown identifier '{}'".format(expr.ID), tok)
                return Expression(tok, "ERROR")

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

            if (hasattr(expr, "text") and expr.text == "ERROR"):
                return Expression(tok, "ERROR")

            if isinstance(expr, Reference) and not expr.ref:
                Exception(
                    'ERROR', "Unknown identifier '{}'".format(expr.ID), tok)
                return Expression(tok, "ERROR")

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

            if (hasattr(exprL, "text") and exprL.text == "ERROR"):
                return Expression(tok, "ERROR")

            if isinstance(exprL, Reference) and not exprL.ref:
                Exception(
                    'ERROR', "Unknown identifier '{}'".format(exprL.ID), tok)
                return Expression(tok, "ERROR")

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

            if (hasattr(exprC, "text") and exprC.text == "ERROR"):
                return Expression(tok, "ERROR")

            if isinstance(exprC, Reference) and not exprC.ref:
                Exception(
                    'ERROR', "Unknown identifier '{}'".format(exprC.ID), tok)
                return Expression(tok, "ERROR")

            if expr_type is None:
                Exception("ERROR", "Expression has no type", tok)

                return Expression(tok, "ERROR")

            else:
                top = ctx.top.text

                if top == '?':
                    return TernaryOPExpression(tok, exprL, exprC, exprR)

                elif expr_type in PrimitiveTypes:
                    otop = {'>': '<', '<': '>'}[top]
                    exprL = BinaryOPExpression(tok, exprL, top, exprC)
                    exprR = BinaryOPExpression(tok, exprC, otop, exprR)
                    return BinaryOPExpression(tok, exprL, '&&', exprR)

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
            ID = str(ID)
            return Reference(
                ctx.start, self.scope[-1].get_symbol(ctx.start, ID), ID)

        if ctx.literal():
            return self.visitLiteral(ctx.literal())

        return self.visitChildren(ctx)

    def visitLiteral(self, ctx: Wappa.LiteralContext) -> Literal:
        text = ctx.getText()

        if ctx.integerLiteral():
            return Literal(ctx.start, text, IntType)

        if ctx.floatLiteral():
            return Literal(ctx.start, text, DoubleType)

        if ctx.stringLiteral():
            return Literal(ctx.start, text, StringType)

        if ctx.BOOL_LITERAL():
            return Literal(ctx.start, text, BoolType)

        if ctx.NIL_LITERAL():
            return Literal(ctx.start, text, NilType)

        Exception("FATAL", "Unhandled Literal: {}".format(ctx.getText()),
                  ctx.start)

        return Literal(ctx.start, text, NilType)

    def visitTypeOrUnit(self, ctx: Wappa.TypeOrUnitContext) -> WappaType:
        return self.visitTypeExpression(ctx.typeExpression())

    def visitTypeExpression(
            self, ctx: Wappa.TypeExpressionContext) -> WappaType:
        if ctx.bop is not None:
            # bop = ctx.bop.text
            pass

            # if bop == '&':
            #     return Intersection
            # elif bop=='|':
            #     return Union

        else:
            return self.visitTypeName(ctx.typeName())

    def visitTypeName(self, ctx: Wappa.TypeNameContext) -> WappaType:
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
