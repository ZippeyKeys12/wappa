from typing import Dict, Optional, Tuple

from src.structs.Field import Field
from src.structs.Function import Function
from src.util import Exception


class Class:
    def __init__(self, ID: str, parent: str,
                 modifiers:
                 Tuple[Optional[str], Optional[str], Optional[str]]):
        self.ID = ID
        self.parent = parent
        self.modifiers = modifiers
        self.fields: Dict[str, Field] = {}
        self.functions: Dict[str, Function] = {}

    def add_member(self, ctx, ID, new_member):
        if ID in self.functions.keys() or ID in self.fields.keys():
            Exception('Conflicting declaration of "{}${}"'.format(
                self.ID, ID), ctx.start)

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
            ID = "{} : {}".format(ID, self.parent)

        # modifiers = filter(lambda x: x is not None, self.modifiers)
        members = self.fields.copy()
        members.update(self.functions)

        return """
            class {} {} {{
                {}
            }}
        """.format(ID, self.modifiers[2],
                   "\n".join((f() for f in members.values())))

    def __str__(self):
        return "{} {}".format(",".join(filter(
            lambda x: x is not None, self.modifiers
        )), self.ID)
