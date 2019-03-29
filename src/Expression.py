class Expression:
    def __init__(self, text):
        self.text = text

    def __call__(self) -> str:
        return self.text
