from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Tuple

import llvmlite.ir as ir

from ..gen.Wappa import Token
from .Field import Field
from .Type import WappaType

if TYPE_CHECKING:
    from .Interface import Interface
    from .Scope import Scope, Symbol
    from .Symbols import SymbolTable


class Class(WappaType):
    def __init__(
        self, scope: Scope, ID: str, parent: Class,
        interfaces: List[Interface],
        modifiers: Tuple[Optional[str], Optional[str], Optional[str]]
    ):
        self.interfaces = interfaces.copy()
        interfaces.append(parent)

        WappaType.__init__(self, ID, supertypes=interfaces)

        self.scope = scope
        scope.owner = self
        self.parent = parent
        self.modifiers = modifiers

    def get_member(self, tok: Token, ID: str) -> Symbol:
        ret = self.scope.get_symbol(tok, ID, not self.parent)

        if not ret and self.parent:
            return self.parent.get_member(tok, ID)

        return ret

    def compile(self, module: ir.Module, builder: ir.IRBuilder,
                symbols: SymbolTable) -> ir.Value:
        ID = self.ID

        if self.parent:
            ID = "{} : {}".format(ID, self.parent.ID)

        # modifiers = filter(lambda x: x is not None, self.modifiers)

        symbols = self.scope.symbols(values=True)

        for s in symbols:
            if isinstance(s, Field):
                pass

        data = ID, self.modifiers[2], " ".join(
            [f.compile(minify) for f in symbols])

        if minify:
            return "class {} {}{{{}}}".format(*data)

        return """
            class {} {} {{
                {}
            }}
        """.format(*data)
