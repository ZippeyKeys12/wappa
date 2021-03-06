from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

import llvmlite.ir as ir

if TYPE_CHECKING:
    from .Scope import Scope
    from .Statement import Statement
    from .Symbols import SymbolTable


class Block:
    def __init__(self, scope: Scope, statements: Iterable[Statement]):
        self.scope = scope
        self.statements = statements

    def compile(self, module: ir.Module, builder: ir.IRBuilder,
                symbols: SymbolTable) -> ir.Value:
        for s in self.statements:
            s.compile(module, builder, symbols)
