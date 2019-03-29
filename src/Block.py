from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable

if TYPE_CHECKING:
    from src.Statement import Statement


class Block:
    def __init__(self, statements: Iterable[Statement]):
        self.statements = statements

    def __call__(self) -> str:
        statements: Any = self.statements
        if statements is not None:
            statements = "".join((s() for s in statements))
        else:
            statements = ""

        return """
            {{
                {}
            }}
        """.format(statements)
