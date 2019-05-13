import llvmlite.ir as ir

from src.structs.Symbols import SymbolTable
from src.structs.Type import WappaType


class Variable:
    def __init__(self, ID: str, var_type: WappaType):
        self.ID = ID
        self.var_type = var_type

    def type_of(self) -> WappaType:
        return self.var_type
