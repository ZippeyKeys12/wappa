from __future__ import annotations

from typing import TYPE_CHECKING, List

import llvmlite.ir as ir

from ..IDGenerator import IDGenerator

if TYPE_CHECKING:
    from ..gen.Wappa import Token
    from ..TypeSystem import TypeSolver
    from .Scope import Symbol


class WappaType:
    tsolver: TypeSolver = None
    idgen: IDGenerator = IDGenerator()

    def __init__(self, ID: str, ir_type: ir.Value = None,
                 supertypes: List[WappaType] = []):
        if WappaType.tsolver is None:
            raise AssertionError("'tsolver' has not been set")

        self.ID = ID
        self.ir_type = ir_type
        self.supertypes = supertypes

    def is_a(self, other: WappaType) -> bool:
        if self is other:
            return True

        for stype in self.supertypes:
            if stype.is_a(other):
                return True

        return False

    def get_symbol(self, tok: Token, ID: str) -> Symbol:
        raise NotImplementedError(
            "'get_symbol' not implemented for {}".format(type(self)))

    def __eq__(self, value):
        if not isinstance(value, WappaType):
            return False

        return self.is_a(value) and value.is_a(self)

    def __hash__(self):
        return self.ID.__hash__()
