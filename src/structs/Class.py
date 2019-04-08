from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Tuple  # noqa

from src.gen.Wappa import Token
from src.util import Exception

if TYPE_CHECKING:
    from src.structs.Scope import Scope


class Class:
    def __init__(self, scope: Scope, ID: str, parent: str,
                 modifiers:
                 Tuple[Optional[str], Optional[str], Optional[str]]):
        self.scope = scope
        scope.owner = self
        self.ID = ID
        self.parent = parent
        self.modifiers = modifiers

    def get_member(self, tok: Token, name: str, ID: str):
        try:
            return self.fields[ID]
        except KeyError:
            return self.functions[ID]
        except KeyError:
            Exception(
                'ERROR', '{} does not have attribute: {}'.format(name, ID),
                tok)

    def __call__(self) -> str:
        ID = self.ID
        if self.parent is not None:
            ID = "{} : {}".format(ID, self.parent)

        # modifiers = filter(lambda x: x is not None, self.modifiers)

        return """
            class {} {} {{
                {}
            }}
        """.format(ID, self.modifiers[2],
                   "\n".join((f() for f in self.scope.symbols(keys=False))))

    def __str__(self):
        return "{} {}".format(",".join(filter(
            lambda x: x is not None, self.modifiers
        )), self.ID)
