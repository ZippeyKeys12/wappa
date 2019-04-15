from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable

if TYPE_CHECKING:
    from src.structs.Scope import Scope
    from src.structs.Statement import Statement


class Block:
    def __init__(self, scope: Scope, statements: Iterable[Statement]):
        self.scope = scope
        self.statements = statements

    def compile(self, minify: bool = False) -> str:
        statements: Any = self.statements
        if statements is not None:
            statements = "".join([s.compile(minify) for s in statements])
        else:
            statements = ""

        if minify:
            return "{{{}}}".format(statements)

        return """
            {{
                {}
            }}
        """.format(statements)
