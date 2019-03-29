class Expression:
    def __init__(self, text):
        self.text = text

    def __call__(self) -> str:
        return self.text


class BinaryOPExpression(Expression):
    def __init__(self, exprL: Expression, bop, exprR: Expression):
        self.exprL = exprL
        self.bop = bop
        self.exprR = exprR

    def __call__(self) -> str:
        bop = self.bop
        exprL = self.exprL()
        exprR = self.exprR()

        if bop in ['**', '*', '/', '%', '+', '-', '<<', '>>', '>>>', '<=',
                   '>=', '<', '>', 'is', '&', '^', '|', '&&', '||', '=', '+=',
                   '-=', '*=', '/=', '&=', '|=', '^=', '<<=', '>>=', '>>>=',
                   '%=']:
            return "({} {} {})".format(exprL, bop, exprR)

        converter = {
            '<=>': '<>=',
            '===': '==',
            '!==': '!='
        }
        if bop in converter.keys():
            return "({} {} {})".format(exprL, converter[bop], exprR)

        if bop == '|>':
            return "({} ({}))".format(exprL, exprR)

        if bop == '**=':
            return "({0} = {0} ** {1})".format(exprL, exprR)

        else:
            print("Error: Unhandled Binary Operator {}".format(bop))
            return bop


class TernaryOPExpression(Expression):
    def __init__(self, exprCond: Expression,
                 exprIf: Expression, exprElse: Expression):
        self.exprCond = exprCond
        self.exprIf = exprIf
        self.exprElse = exprElse

    def __call__(self) -> str:
        return "({} ? {} : {})".format(
            self.exprCond, self.exprIf, self.exprElse)
