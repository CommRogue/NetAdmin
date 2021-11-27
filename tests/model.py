class CalcModel:
    @staticmethod
    def evaluateExpression(exp):
        try:
            return str(eval(exp))
        except Exception as e:
            return "Error while evaluating expression. Check syntax and try again...."