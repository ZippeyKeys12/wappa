from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Tuple

from .Class import Class

if TYPE_CHECKING:
    from .Scope import Scope


class Interface(Class):
    def __init__(self, scope: Scope, ID: str, parents: List[Interface],
                 modifiers: Tuple[Optional[str], Optional[str]]):
        Class.__init__(self, scope, ID, None, parents, modifiers)
