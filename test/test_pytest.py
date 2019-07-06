from compiler.structs.Type import WappaType
from compiler.TypeSystem import (AnyType, BoolType, ByteType, DoubleType,
                                 FloatType, IntType, LongType, ShortType,
                                 StringType, TypeSolver)


def test_linearize():
    ttype = WappaType(
        "Test Type", supertypes=[BoolType, StringType])

    assert TypeSolver().linearize_hierarchy(
        ttype) == [ttype, BoolType, ByteType, ShortType, IntType, LongType,
                   FloatType, DoubleType, StringType, AnyType]


def test_nca():
    assert TypeSolver().ncas((BoolType, StringType)) == [AnyType]


def test_shared():
    assert TypeSolver().shared_hierarchy((BoolType, FloatType)) == [
        ByteType, IntType, FloatType, DoubleType, AnyType]


def test_simplfied():
    tsolver = TypeSolver()
    hierarchy = tsolver.linearize_hierarchy(WappaType(
        "Test Type", supertypes=[BoolType, StringType]))[1:]

    assert tsolver._TypeSolver__simplify_hierarchy(hierarchy) == [
        BoolType, StringType]
