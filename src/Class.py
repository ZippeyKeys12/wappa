from typing import Any, Dict, Optional, Tuple

ostr = Optional[str]


class Class:
    def __init__(self, ID: str, parent: str, modifiers: Tuple[ostr, ostr]):
        self.ID = ID
        self.parent = parent
        self.modifiers = modifiers
        self.fields: Dict[str, Any] = {}
        self.functions: Dict[str, Any] = {}

    def add(self, newMember):
        pass

    def remove(self, ID: str):
        try:
            del self.fields[ID]
        except KeyError:
            del self.functions[ID]

    def compile(self, ID: str) -> str:
        if self.parent is not None:
            ID += ":{}".format(self.parent)

        # modifiers = filter(lambda x: x is not None, self.modifiers)
        members = (f.compile() for f in list(
            self.fields.values())+list(self.functions.values()))

        return """
            class {} {{
                {}
            }}
        """.format(ID, "\n".join(members))

    def __str__(self):
        return "{} {}".format(",".join(filter(
            lambda x: x is not None, self.modifiers
        )), self.ID)


del ostr
