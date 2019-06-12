from __future__ import annotations

from typing import Dict, List, Optional

import llvmlite.ir as ir


class SymbolTable:
    def __init__(self, parent: SymbolTable = None):
        self.parent = parent
        self.symbol_table: Dict[str, ir.Value] = {}
        self.element_table: Dict[str, List[str]] = {}
        self.function_table: Dict[str, Dict[str, ir.Function]]

    def add_symbol(
            self, ID: str, symbol: ir.Value, elements: List[str] = [],
            functions: Dict[str, ir.Function] = {}):
        if ID in self.symbol_table.keys():
            print("ERROR - 'add_symbol', {} already exists".format(ID))

        self.symbol_table[ID] = symbol

        if len(elements) != 0:
            self.element_table[ID] = elements

        if len(functions) != 0:
            self.function_table[ID] = functions

    def get_symbol(self, ID: str) -> Optional[ir.Value]:
        try:
            return self.symbol_table[ID]
        except KeyError:
            if self.parent:
                return self.parent.get_symbol(ID)

    def get_elements(self, ID: str) -> Optional[List[str]]:
        try:
            return self.element_table[ID]
        except KeyError:
            if self.parent:
                return self.parent.get_elements(ID)

    def get_functions(self, ID: str) -> Optional[Dict[str, ir.Function]]:
        try:
            return self.function_table[ID]
        except KeyError:
            if self.parent:
                return self.parent.get_functions(ID)
