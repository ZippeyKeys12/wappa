from __future__ import annotations

from typing import Dict, Optional

import llvmlite.ir as ir


class SymbolTable:
    def __init__(self, parent: SymbolTable = None):
        self.parent = parent
        self.symbol_table: Dict[str, ir.Value] = {}

    def add_symbol(self, ID, symbol):
        if ID in self.symbol_table.keys():
            print("ERROR - add_symbol")

        self.symbol_table[ID] = symbol

    def set_symbol(self, ID, symbol):
        if ID not in self.symbol_table.keys():
            print("ERROR - set_symbol")

        self.symbol_table[ID] = symbol

    def get_symbol(self, ID) -> Optional[ir.Value]:
        try:
            return self.symbol_table[ID]
        except KeyError:
            if self.parent:
                return self.parent.get_symbol(ID)
