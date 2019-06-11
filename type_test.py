import time

from src.structs.Type import WappaType
from src.TypeSystem import BoolType, FloatType, StringType, TypeSolver

ITERATIONS = 1000000


def time_linearize(tsolver: TypeSolver):
    test_type = WappaType(
        "Test Type", supertypes=[BoolType, StringType])

    start = time.time()

    for _ in range(ITERATIONS):
        ans = tsolver.linearize_hierarchy(test_type)

    end = time.time()

    print("Took {} s".format(end - start))
    print([x.ID for x in ans])


def time_nca(tsolver: TypeSolver):
    start = time.time()

    for _ in range(ITERATIONS):
        ans = tsolver.ncas((BoolType, StringType))

    end = time.time()

    print("Took {} s".format(end - start))
    print([x.ID for x in ans])


def time_shared(tsolver: TypeSolver):
    start = time.time()

    for _ in range(ITERATIONS):
        ans = tsolver.shared_hierarchy((BoolType, FloatType))

    end = time.time()

    print("Took {} s".format(end - start))
    print([x.ID for x in ans])


def time_simplfied(tsolver: TypeSolver):
    hierarchy = tsolver.linearize_hierarchy(WappaType(
        "Test Type", supertypes=[BoolType, StringType]))[1:]
    start = time.time()

    for _ in range(ITERATIONS):
        ans = tsolver._TypeSolver__simplify_hierarchy(hierarchy)

    end = time.time()

    print("Took {} s".format(end - start))
    print([x.ID for x in ans])


if __name__ == "__main__":
    tsolver = TypeSolver()

    time_linearize(tsolver)

    time_nca(tsolver)

    time_shared(tsolver)

    time_simplfied(tsolver)
