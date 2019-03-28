from typing import List, Tuple

from src.Statement import Statement


class Function:
    def __init__(self, ID: str, modifiers: Tuple[bool, bool, str, str],
                 parameters: List[Tuple[str, str]], ret_type: str,
                 block: List[Statement]):
        self.ID = ID
        self.parameters = parameters
        self.ret_type = ret_type
        self.block = block

    def inline(self, args: List[str]) -> str:
        return ""

    def __call__(self) -> str:
        parameters = ",".join((" ".join(x[::-1]) for x in self.parameters))
        return """
            {} {} ({}) {{
                {}
            }}
        """.format(self.ret_type, self.ID, parameters, ";".join(self.block))
