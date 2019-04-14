from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Tuple

if TYPE_CHECKING:
    from src.structs import Block, Class


class Function:
    def __init__(self, ID: str,
                 modifiers: Tuple[bool, bool, Optional[str], Optional[str]],
                 parameters: List[Tuple[str, Class]],
                 ret_type: Optional[Class], block: Block):
        self.scope = block.scope
        self.ID = ID
        self.parameters = parameters
        self.ret_type = ret_type
        self.block = block

    def inline(self, args: List[str]) -> str:
        return ""

    def compile(self, minify: bool = False) -> str:
        parameters = ",".join(
            ("{} {}".format(x[0], x[1].ID) for x in self.parameters))

        ret_type = "void"
        if self.ret_type:
            ret_type = self.ret_type.ID

        data = (ret_type, self.ID, parameters, self.block.compile(minify))

        if minify:
            return "{} {}({}){}".format(*data)

        return """
            {} {} ({}) {}
        """.format(*data)


class NativeFunction(Function):
    def __init__(self, ID, parameters: List[Tuple[str, Class]],
                 ret_type: Optional[Class]):
        self.ID = ID
        self.parameters = parameters
        self.ret_type = ret_type

    def inline(self, args: List[str]) -> str:
        return ""

    def compile(self, minify: bool = False) -> str:
        return ""
