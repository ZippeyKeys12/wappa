class WappaType:
    def __init__(self, ID: str):
        self.ID = ID

    def __eq__(self, value):
        return value == self.ID


IntType = WappaType("Int")


FloatType = WappaType("Float")


StringType = WappaType("String")


BooleanType = WappaType("Boolean")


NilType = WappaType("Nil")


class TypeType(WappaType):
    def __init__(self, ref: WappaType):
        self.ref = ref

        WappaType.__init__(self, ref.ID)

    def __eq__(self, value) -> bool:
        return value is self.ref
