from __future__ import annotations

from functools import lru_cache
from typing import Iterable, List, Optional, Tuple

import llvmlite.ir as ir

from .structs.Type import WappaType
from .util import methoddispatch


class TypeSolver:
    @lru_cache()
    def linearize_hierarchy(self, wtype: WappaType) -> Iterable[WappaType]:
        """Returns the supertypes, linearized, increasing in distance"""

        supertypes = []

        supertypes.append(wtype)

        for stype in wtype.supertypes:
            if stype in supertypes:
                continue

            for sstype in self.linearize_hierarchy(stype):
                if sstype not in supertypes:
                    for index, ssstype in enumerate(supertypes):
                        if sstype.is_a(ssstype):
                            supertypes.insert(index, stype)
                            break
                    else:
                        supertypes.append(sstype)

        return supertypes

    @lru_cache()
    def shared_hierarchy(
            self, wtypes: Iterable[WappaType]) -> List[WappaType]:
        """Returns the intersection of their linearized hierarchies"""

        if len(wtypes) < 2:
            raise ValueError("'nce' Must have at least 2 types given")

        ret = self.linearize_hierarchy(wtypes[0])

        for wtype in wtypes[1:]:
            for r in ret:
                if not wtype.is_a(r):
                    ret.remove(r)

        return ret

    @methoddispatch
    def ncas(self, wtypes) -> Optional[WappaType]:
        """Returns the nearest common ancestor"""

        raise TypeError(
            "'wtypes' must be an [list, set, tuple], is {}".format(
                type(wtypes)))

    @ncas.register(list)
    @ncas.register(set)
    def _(self, wtypes: Iterable[WappaType]) -> Optional[WappaType]:
        return self.ncas(tuple(wtypes))

    @ncas.register(tuple)
    @lru_cache()
    def _(self, wtypes: Tuple[WappaType]) -> Optional[WappaType]:
        if len(wtypes) < 2:
            raise ValueError("'nca' Must have at least 2 types given")

        ret = [wtypes[0]]
        for wtype in wtypes[1:]:
            tmp = []

            for ret_val in ret:
                tmp.extend(self._ncas(ret_val, wtype))

            ret = self.__simplify_hierarchy(tmp)

            if ret == [] or ret[0] == AnyType:
                return ret

        return ret

    @lru_cache()
    def _ncas(self, wtype_1: WappaType, wtype_2: WappaType
              ) -> List[WappaType]:
        """Returns the nearest common ancestor"""

        ret = []

        if wtype_1.is_a(wtype_2):
            ret.append(wtype_2)

        elif wtype_2.is_a(wtype_1):
            ret.append(wtype_1)

        else:
            genealogy = self.linearize_hierarchy(wtype_1)
            for stype in self.linearize_hierarchy(wtype_2):
                if (stype in genealogy and
                        (len(ret) == 0 or not ret[-1].is_a(stype))):
                    ret.append(stype)

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

    @methoddispatch
    def __simplify_hierarchy(self, wtypes) -> List[WappaType]:
        """Returns a simplified hierarchy"""

        raise TypeError(
            "'wtypes' must be an [list, set, tuple], is {}".format(
                type(wtypes)))

    @__simplify_hierarchy.register(list)
    @__simplify_hierarchy.register(set)
    def _(self, wtypes: Iterable[WappaType]) -> List[WappaType]:
        return self.__simplify_hierarchy(tuple(wtypes))

    @__simplify_hierarchy.register(tuple)
    @lru_cache()
    def _(self, wtypes: Tuple[WappaType]) -> List[WappaType]:
        ret = [wtypes[0]]

        for item in wtypes[1:]:
            for index, it in enumerate(ret):
                if item.is_a(it):
                    ret.remove(it)
                    ret.insert(index, item)

                elif it.is_a(item):
                    continue

                else:
                    ret.append(item)

        return ret

    def __intersect_lists(self, list_1: list, list_2: list) -> list:
        """Returns the items in both lists"""

        ret = []

        for item in list_1:
            if item in list_2:
                ret.append(item)

        return ret


if WappaType.tsolver is None:
    WappaType.tsolver = TypeSolver()

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

    def is_a(self, other: WappaType) -> bool:
        pass

    def __hash__(self):
        return super().__hash__() ^ "typetype".__hash__()


class IntersectionType(WappaType):
    def __init__(self, ID: str = '', wtypes: List[WappaType] = []):
        WappaType.__init__(self, ID, supertypes=wtypes)

    def __hash__(self):
        ret = super.__hash__()

        for stype in self.supertypes:
            ret ^= stype.__hash__()

        return ret ^ "intersection".__hash__()


class UnionType(WappaType):
    def __init__(self, ID: str = '', wtypes: List[WappaType] = []):
        if ID == '':
            ID = WappaType.idgen.generate_id()

        WappaType.__init__(self, ID)

        self.options = wtypes

    def is_a(self, other: WappaType) -> bool:
        nca = WappaType.tsolver.ncas((self, other))

        if nca is None:
            return False

        return nca.is_a(other)

    def __hash__(self):
        ret = super.__hash__()

        for stype in self.options:
            ret ^= stype.__hash__()

        return ret ^ "intersection".__hash__()
