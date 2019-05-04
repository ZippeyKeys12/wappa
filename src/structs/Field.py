from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Tuple

if TYPE_CHECKING:
    from src.structs.Expression import Expression
    from src.structs.Type import WappaType


class Field:
    def __init__(self, tok, ID: str, object_type: WappaType, access_type: str,
                 modifiers: Tuple[str] = None, value: Expression = None):
        self.tok = tok
        self.ID = ID
        self.object_type = object_type
        self.access_type = access_type
        self.modifiers = modifiers
        self.value = value

    def type_of(self) -> Optional[WappaType]:
        if self.object_type:
            return self.object_type

        if self.value is not None:
            return self.value.type_of()

        return None

    def compile(self, minify: bool = False) -> str:
        if self.object_type is None:
            self.object_type = self.value.type_of().ID
        return "{} {};".format(self.object_type, self.ID)
