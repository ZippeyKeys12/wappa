from typing import List, Tuple

from Statement import Statement

arg_type = Tuple[str, str]


class Function:
    def __init__(self, ID: str, args: List[arg_type], ret_type: str,
                 stnts: List[Statement]):
        self.ID = ID
        self.statements = stnts

    def inline(self, args: List[str]) -> str:
        return ""

    def compile(self, ID: str) -> str:
        return "{}{}".format(ID, ";".join(self.statements))
