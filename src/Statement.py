class Statement:
    def __init__(self, content: str):
        self.content = content

    def compile(self):
        return self.content
