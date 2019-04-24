from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from src.structs.Expression import Expression
    from src.structs.Type import WappaType


class Field:
    def __init__(self, ID: str, object_type: WappaType, access_type: str,
                 modifiers: Tuple[str] = None, value: Expression = None):
        self.ID = ID
        self.object_type = object_type
        self.access_type = access_type
        self.modifiers = modifiers
        self.value = value

    def compile(self, minify: bool = False) -> str:
        return ""
