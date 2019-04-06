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
    def __init__(self, exprL: Expression, top: str,
                 exprC: Expression, exprR: Expression):
        self.exprL = exprL
        self.top = top
        self.exprC = exprC
        self.exprR = exprR

    def __call__(self) -> str:
        top = self.top
        exprL = self.exprL()
        exprC = self.exprC()
        exprR = self.exprR()

        if top == "?":
            return "({} ? {} : {})".format(exprL, exprC, exprR)

        elif top == "<":
            return "({0} < {1} && {1} < {2})".format(exprL, exprC, exprR)

        elif top == ">":
            return "({0} > {1} && {1} > {2})".format(exprL, exprC, exprR)

        else:
            print("Error: Unhandled Ternary Operator {}".format(top))
            return top
