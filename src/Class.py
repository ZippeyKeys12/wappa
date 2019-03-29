from typing import Dict, Optional, Tuple

from src.Field import Field
from src.Function import Function


class Class:
    def __init__(self, ID: str, parent: str,
                 modifiers: Tuple[Optional[str], Optional[str]]):
        self.ID = ID
        self.parent = parent
        self.modifiers = modifiers
        self.fields: Dict[str, Field] = {}
        self.functions: Dict[str, Function] = {}

    def add_member(self, ID, new_member):
        if isinstance(new_member, Function):
            self.functions[ID] = new_member
        elif isinstance(new_member, Field):
            self.fields[ID] = new_member

    def remove_member(self, ID: str):
        try:
            del self.fields[ID]
        except KeyError:
            del self.functions[ID]

    def __call__(self) -> str:
        ID = self.ID
        if self.parent is not None:
            ID = "{}:{}".format(ID, self.parent)

        # modifiers = filter(lambda x: x is not None, self.modifiers)
        members = self.fields.copy()
        members.update(self.functions)

        # print(self.functions["IDNEIT"].compile("IDNEIT"))

        return """
            class {} {{
                {}
            }}
        """.format(ID, "\n".join((f() for f in members.values())))

    def __str__(self):
        return "{} {}".format(",".join(filter(
            lambda x: x is not None, self.modifiers
        )), self.ID)
