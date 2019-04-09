from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable

if TYPE_CHECKING:
    from src.structs import Scope, Statement


class Block:
    def __init__(self, scope: Scope, statements: Iterable[Statement]):
        self.scope = scope
        self.statements = statements

    def compile(self) -> str:
        statements: Any = self.statements
        if statements is not None:
            statements = "".join((s.compile() for s in statements))
        else:
            statements = ""

        return """
            {{
                {}
            }}
        """.format(statements)
