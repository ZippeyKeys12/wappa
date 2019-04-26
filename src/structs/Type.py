from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.gen.Wappa import Token
    from src.structs.Scope import Symbol


class WappaType:
    def __init__(self, ID: str):
        self.ID = ID

    def get_member(self, tok: Token, ID: str) -> Symbol:
        raise NotImplementedError(
            "'get_member' not implemented for {}".format(type(self)))

    def __eq__(self, value):
        return value == self.ID


IntType = WappaType("Int")


FloatType = WappaType("Float")


StringType = WappaType("String")


BoolType = WappaType("Boolean")


NilType = WappaType("Nil")

PrimitiveTypes = [IntType, FloatType, StringType, BoolType, NilType]


class TypeType(WappaType):
    def __init__(self, ref: WappaType):
        self.ref = ref

        WappaType.__init__(self, ref.ID)

    def __eq__(self, value) -> bool:
        return value is self.ref
