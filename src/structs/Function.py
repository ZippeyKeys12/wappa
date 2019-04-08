from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    from src.structs.Block import Block


class Function:
    def __init__(self, ID: str, modifiers: Tuple[bool, bool, str, str],
                 parameters: List[Tuple[str, str]], ret_type: str,
                 block: Block):
        self.ID = ID
        self.parameters = parameters
        self.ret_type = ret_type
        self.block = block

    def inline(self, args: List[str]) -> str:
        return ""

    def compile(self) -> str:
        parameters = ",".join((" ".join(x[::-1]) for x in self.parameters))
        return """
            {} {} ({}) {}
        """.format(self.ret_type, self.ID, parameters, self.block.compile())
