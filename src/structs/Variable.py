from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import llvmlite.ir as ir

from .Type import WappaType

if TYPE_CHECKING:
    from ..gen.Wappa import Token
    from .Scope import Symbol


class Variable:
    def __init__(self, ID: str, var_type: WappaType):
        self.ID = ID
        self.var_type = var_type

    def get_symbol(self, tok: Token, ID: str) -> Symbol:
        return self.type_of().get_symbol(tok, ID)

    def type_of(self) -> WappaType:
        return self.var_type

    @property
    def ir_type(self) -> Optional[ir.Value]:
        try:
            return self.type_of().ir_type
        except AttributeError:
            return None
