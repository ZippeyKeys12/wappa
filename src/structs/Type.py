from __future__ import annotations

from typing import TYPE_CHECKING, List

import llvmlite.ir as ir

if TYPE_CHECKING:
    from src.gen.Wappa import Token
    from src.structs.Scope import Symbol


class WappaType:
    def __init__(self, ID: str, ir_type: ir.Value = None,
                 supertypes: List[WappaType] = []):
        self.ID = ID
        self.ir_type = ir_type
        self.supertypes = supertypes

    def is_a(self, other: WappaType):
        return self == other or other in self.supertypes

    def get_member(self, tok: Token, ID: str) -> Symbol:
        raise NotImplementedError(
            "'get_member' not implemented for {}".format(type(self)))

    def __eq__(self, value):
        return value == self.ID


DoubleType = WappaType("Double", ir.DoubleType())


IntType = WappaType("Int", ir.IntType(32), supertypes=[DoubleType])


StringType = WappaType("String")


BoolType = WappaType("Boolean", ir.IntType(1))


NilType = WappaType("Nil")

UnitType = WappaType("Void")

PrimitiveTypes = [IntType, DoubleType, StringType, BoolType, NilType]


class TypeType(WappaType):
    def __init__(self, ref: WappaType):
        self.ref = ref

        WappaType.__init__(self, ref.ID)

    def __eq__(self, value) -> bool:
        return value is self.ref
