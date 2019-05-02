from src.structs.Type import WappaType


class Variable:
    def __init__(self, ID: str, var_type: WappaType):
        self.var_type = var_type
        self.ID = ID

    def type_of(self) -> WappaType:
        return self.var_type

    # def compile(self, minify: bool = False) -> str:
    #     return ""
