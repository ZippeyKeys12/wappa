from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Tuple  # noqa

from src.gen.Wappa import Token

if TYPE_CHECKING:
    from src.structs import Scope


class Class:
    def __init__(self, scope: Scope, ID: str, parent: Optional[Class],
                 modifiers: Tuple[Optional[str], Optional[str], Optional[str]]
                 ):
        self.scope = scope
        scope.owner = self
        self.ID = ID
        self.parent = parent
        self.modifiers = modifiers

    def get_member(self, tok: Token, name: str, ID: str):
        return self.scope.get_symbol(tok, ID)

    def compile(self, minify: bool = False) -> str:
        ID = self.ID
        if self.parent is not None:
            ID = "{} : {}".format(ID, self.parent.ID)

        # modifiers = filter(lambda x: x is not None, self.modifiers)

        data = ID, self.modifiers[2], " ".join([
            f.compile(minify) for f in self.scope.symbols(values=True)])  # type: ignore # noqa

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
