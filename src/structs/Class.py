from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Tuple

from src.gen.Wappa import Token
from src.structs.Field import Field
from src.structs.Type import WappaType

if TYPE_CHECKING:
    from src.structs.Scope import Scope, Symbol


class Class(WappaType):
    def __init__(self, scope: Scope, ID: str, parent: Optional[Class],
                 modifiers: Tuple[Optional[str], Optional[str], Optional[str]]
                 ):
        WappaType.__init__(self, ID)

        self.scope = scope
        scope.owner = self
        self.parent = parent
        self.modifiers = modifiers

    def get_member(self, tok: Token, name: str, ID: str) -> Symbol:
        return self.scope.get_symbol(tok, ID)

    def compile(self, minify: bool = False) -> str:
        ID = self.ID

        if self.parent:
            ID = "{} : {}".format(ID, self.parent.ID)

        # modifiers = filter(lambda x: x is not None, self.modifiers)

        symbols = self.scope.symbols(values=True)

        for s in symbols:
            if isinstance(s, Field):
                pass

        data = ID, self.modifiers[2], " ".join([
            f.compile(minify) for f in symbols])  # type: ignore # noqa

        if minify:
            return "class {} {}{{{}}}".format(*data)

        return """
            class {} {} {{
                {}
            }}
        """.format(*data)

    def __str__(self):
        return "{} {}".format(",".join(filter(
            lambda x: x is not None, self.modifiers
        )), self.ID)
