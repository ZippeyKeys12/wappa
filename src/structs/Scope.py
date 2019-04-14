from __future__ import annotations

from typing import Dict, List, Tuple, Union

from src.gen.Wappa import Token
from src.structs import Class, Field, Function
from src.util import Exception

Symbol = Union[Class, Field, Function]


class Scope:
    def __init__(self, parent: Scope = None):
        self.parent = parent
        self.symbol_table: Dict[str, Symbol] = {}

    def add_symbol(self, tok: Token, ID: str, symbol: Symbol):
        if ID.lower() in self.symbol_table.keys():
            Exception(
                'ERROR', "Conflicting declaration of '{}'".format(ID), tok)
            print("self:{}".format(self.symbols(values=False)))

        self.symbol_table[ID.lower()] = symbol

    def get_symbol(self, tok: Token, ID: str):
        try:
            return self.symbol_table[ID.lower()]
        except KeyError:
            if self.parent is not None:
                return self.parent.get_symbol(tok, ID)
            else:
                Exception(
                    'ERROR', "Unknown identifier '{}'".format(ID), tok)

    def symbols(self, keys: bool = True, values: bool = True
                ) -> List[Union[str, Symbol, Tuple[str, Symbol]]]:
        if keys and values:
            return [(k, v) for k, v in self.symbol_table.items()]

        if keys:
            return [k for k, v in self.symbol_table.items()]

        if values:
            return [v for k, v in self.symbol_table.items()]

        raise ValueError("At least one of keys or values must be True")

    def depth(self):
        if self.parent:
            return 1 + self.parent.depth()

        return 1
