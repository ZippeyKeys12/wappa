from __future__ import annotations

from typing import Any, Dict


class SymbolTable:
    def __init__(self, parent: SymbolTable = None):
        self.parent = parent
        self.symbol_table: Dict[str, Any] = {}

    def add_symbol(self, ID, symbol):
        if ID in self.symbol_table.keys():
            print("ERROR - add_symbol")

        self.symbol_table[ID] = symbol

    def set_symbol(self, ID, symbol):
        if ID not in self.symbol_table.keys():
            print("ERROR - set_symbol")

        self.symbol_table[ID] = symbol

    def get_symbol(self, ID):
        return self.symbol_table[ID]
