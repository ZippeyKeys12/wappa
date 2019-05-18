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


UnitType = WappaType("Unit", supertypes=[AnyType])


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
        self.ID = ID
        self.supertypes = wtypes

    def is_a(self, other):
        return super().is_a(other)

    def __eq__(self, value):
        return (isinstance(value, IntersectionType)
                and value.supertypes == self.supertypes)


class TypeSolver:
    linearized_hierarchies = {}

    def linearize_hierarchy(self, wtype: WappaType) -> List[WappaType]:
        """Returns the supertypes, linearized, increasing in distance"""

        if wtype.ID in self.linearized_hierarchies.keys():
            return self.linearized_hierarchies[wtype.ID]

        supertypes = []

        supertypes.append(wtype)

        for stype in wtype.supertypes:
            # if stype in supertypes:
            #     continue

            for sstype in self.linearize_hierarchy(stype):
                if sstype not in supertypes:
                    supertypes.append(sstype)

        self.linearized_hierarchies[wtype.ID] = supertypes

        return supertypes

    ncas = {}

    def nca(self, wtype_1: WappaType, wtype_2: WappaType
            ) -> Optional[WappaType]:
        """Returns the nearest common ancestor"""

        if (wtype_1.ID, wtype_2.ID) in self.ncas.keys():
            return self.ncas[(wtype_1.ID, wtype_2.ID)]

        ret = None

        if wtype_1.is_a(wtype_2):
            ret = wtype_2

        elif wtype_2.is_a(wtype_1):
            ret = wtype_1

        else:
            genealogy = self.linearize_hierarchy(wtype_1)
            for stype in self.linearize_hierarchy(wtype_2):
                if stype in genealogy:
                    ret = stype
                    break

        self.ncas[(wtype_1.ID, wtype_2.ID)] = ret

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
