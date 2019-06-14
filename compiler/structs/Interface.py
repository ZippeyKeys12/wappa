from __future__ import annotations

from .Class import Class
from typing import List, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .Scope import Scope


class Interface(Class):
    def __init__(self, scope: Scope, ID: str, parents: List[Interface],
                 modifiers: Tuple[Optional[str], Optional[str]]):
        Class.__init__(self, scope, ID, None, parents, modifiers)
