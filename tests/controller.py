import functools

class CalcController:
    def __init__(self, view, model):
        self.view = view
        self.model = model
        self._connect_signals()

    def _build_expression(self, text):
        exp = self.view.getDisplayText() + text
        self.view.setDisplayText(exp)

    def setResult(self):
        result = self.model.evaluateExpression(self.view.getDisplayText())
        self.view.setDisplayText(result)

    def deleteCharacter(self):
        self.view.setDisplayText(self.view.getDisplayText()[:-1])

    def _connect_signals(self):
        for text, qBtn in self.view.buttons.items():
            if text == "C":
                qBtn.clicked.connect(self.view.clearDisplay)
            elif text == "=":
                qBtn.clicked.connect(self.setResult)
            elif text == "DEL":
                qBtn.clicked.connect(self.deleteCharacter)
            else:
                qBtn.clicked.connect(functools.partial(self._build_expression, text))