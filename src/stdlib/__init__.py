from src.structs.Function import NativeFunction
from src.structs.Scope import Scope


def init_stdlib(scope: Scope):
    scope.add_symbol(None, "print", NativeFunction("console.printf", [], None))
