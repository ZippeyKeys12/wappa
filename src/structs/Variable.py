from typing import Optional

import llvmlite.ir as ir

from .Type import WappaType


class Variable:
    def __init__(self, ID: str, var_type: WappaType):
        self.ID = ID
        self.var_type = var_type

    def type_of(self) -> WappaType:
        return self.var_type

    @property
    def ir_type(self) -> Optional[ir.Value]:
        try:
            return self.type_of().ir_type
        except AttributeError:
            return None
