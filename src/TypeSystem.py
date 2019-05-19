from __future__ import annotations

from typing import Iterable, List, Optional

import llvmlite.ir as ir

from src.structs.Type import WappaType

AnyType = WappaType("Any")
NilType = WappaType("Nil")


NumberType = WappaType("Number", supertypes=[AnyType])

DoubleType = WappaType("Double", ir.DoubleType(), supertypes=[NumberType])
FloatType = WappaType("Float", ir.FloatType(), supertypes=[DoubleType])

LongType = WappaType("Long", ir.IntType(64), supertypes=[FloatType])
IntType = WappaType("Int", ir.IntType(32), supertypes=[LongType])
ShortType = WappaType("Short", ir.IntType(16), supertypes=[IntType])
ByteType = WappaType("Byte", ir.IntType(8), supertypes=[ShortType])


StringType = WappaType("String", supertypes=[AnyType])


BoolType = WappaType("Boolean", ir.IntType(1), supertypes=[ByteType])


ObjectType = WappaType("Object", supertypes=[AnyType])


UnitType = WappaType("Unit", ir.VoidType(), supertypes=[AnyType])


NothingType = WappaType("Nothing")

PrimitiveTypes = [IntType, DoubleType, StringType, BoolType, NilType]


class TypeType(WappaType):
    def __init__(self, ref: WappaType):
        self.ref = ref

        WappaType.__init__(self, ref.ID)

    def __eq__(self, value) -> bool:
        return value is self.ref


class IntersectionType(WappaType):
    def __init__(self, ID: str, wtypes: Iterable[WappaType]):
        WappaType.__init__(self, ID, supertypes=list(wtypes))

    def __eq__(self, value) -> bool:
        if self is value:
            return True

        if not isinstance(value, IntersectionType):
            return False

        if len(value.supertypes) != len(self.supertypes):
            return False

        for stype in self.supertypes:
            if stype not in value.supertypes:
                return False

        return True


class UnionType(WappaType):
    def __init__(self, ID: str, wtypes: Iterable[WappaType]):
        WappaType.__init__(self, ID)

        self.options = wtypes

    def is_a(self, tsolver: TypeSolver, other: WappaType) -> bool:
        nca = tsolver.nca(self, other)

        if nca is None:
            return False

        return nca.is_a(other)

    def __eq__(self, value):
        if self is value:
            return True

        if not isinstance(value, IntersectionType):
            return False

        if len(value.supertypes) != len(self.supertypes):
            return False

        for stype in self.supertypes:
            if stype not in value.supertypes:
                return False

        return True


class TypeSolver:
    linearized_hierarchies = {}

    def linearize_hierarchy(self, wtype: WappaType) -> Iterable[WappaType]:
        """Returns the supertypes, linearized, increasing in distance"""

        if wtype.ID in self.linearized_hierarchies.keys():
            return self.linearized_hierarchies[wtype.ID]

        supertypes = []

        supertypes.append(wtype)

        for stype in wtype.supertypes:
            if stype in supertypes:
                continue

            for sstype in self.linearize_hierarchy(stype):
                if sstype not in supertypes:
                    for index, ssstype in enumerate(supertypes):
                        if sstype.is_a(self, ssstype):
                            supertypes.insert(index, stype)
                            break
                    else:
                        supertypes.append(sstype)

        self.linearized_hierarchies[wtype.ID] = supertypes

        return supertypes

    shared_hierarchies = {}

    def shared_hierarchy(
            self, *wtypes: Iterable[WappaType]) -> List[WappaType]:
        """Returns the intersection of their linearized hierarchies"""

        if len(wtypes) < 2:
            raise ValueError("'nce' Must have at least 2 types given")

        ret = self.linearize_hierarchy(wtypes[0])

        for wtype in wtypes[1:]:
            for r in ret:
                if not wtype.is_a(self, r):
                    ret.remove(r)

        return ret

    ncas = {}

    def nca(self, *wtypes: Iterable[WappaType]) -> Optional[WappaType]:
        """Returns the nearest common ancestor"""

        if len(wtypes) < 2:
            raise ValueError("'nca' Must have at least 2 types given")

        ret = wtypes[0]
        for wtype in wtypes[1:]:
            ret = self._nca(ret, wtype)

            if ret is None or ret == AnyType:
                return ret

        return ret

    def _nca(self, wtype_1: WappaType, wtype_2: WappaType
             ) -> Optional[WappaType]:
        """Returns the nearest common ancestor"""

        key = (wtype_1.ID, wtype_2.ID)
        if key in self.ncas.keys():
            return self.ncas[key]

        ret = None

        if wtype_1.is_a(self, wtype_2):
            ret = wtype_2

        elif wtype_2.is_a(self, wtype_1):
            ret = wtype_1

        else:
            genealogy = self.linearize_hierarchy(wtype_1)
            for stype in self.linearize_hierarchy(wtype_2):
                if stype in genealogy:
                    ret = stype
                    break

        self.ncas[key] = ret

        return ret

    # TODO: After protocols/interfades/multiple inheritance
    # def intersect(self, wtypes: List[WappaType]) -> Optional[WappaType]:
    #     """Generates intersection of two types, if possible"""

    #     if len(wtypes) < 2:
    #         raise ValueError("List must have at least 2 elements")

    #     prev = wtypes[0]
    #     for wtype in wtypes[1:]:
    #         if self.nca(prev, wtype) is None:
    #             return None

    #         prev = wtype
