from __future__ import annotations

from typing import TYPE_CHECKING, List

import llvmlite.ir as ir

if TYPE_CHECKING:
    from ..gen.Wappa import Token
    from .Scope import Symbol
    from ..TypeSystem import TypeSolver


class WappaType:
    def __init__(self, ID: str, ir_type: ir.Value = None,
                 supertypes: List[WappaType] = []):
        self.ID = ID
        self.ir_type = ir_type
        self.supertypes = supertypes

    def is_a(self, tsolver: TypeSolver, other: WappaType) -> bool:
        if self is other:
            return True

        for stype in self.supertypes:
            if stype.is_a(tsolver, other):
                return True

        return False

    def get_member(self, tok: Token, ID: str) -> Symbol:
        raise NotImplementedError(
            "'get_member' not implemented for {}".format(type(self)))

    def __eq__(self, value):
        return value == self.ID

    def __hash__(self):
        return self.ID.__hash__()
