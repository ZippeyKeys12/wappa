from src.structs.Type import WappaType


class Variable:
    def __init__(self, var_type: WappaType, ID: str):
        self.var_type = var_type
        self.ID = ID

    def compile(self, minify: bool = False) -> str:
        return ""
