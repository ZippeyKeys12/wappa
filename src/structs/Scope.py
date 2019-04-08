from __future__ import annotations

from typing import Dict, Iterator, Tuple, Union

from src.gen.Wappa import Token
from src.structs.Class import Class
from src.structs.Field import Field
from src.structs.Function import Function

Symbol = Union[Class, Field, Function]


class Scope:
    def __init__(self, owner: Symbol = None, parent: Scope = None):
        self.owner = owner
        self.parent = parent
        self.symbol_table: Dict[str, Symbol] = {}

    def add_symbol(self, tok: Token, ID: str, symbol: Symbol):
        if ID in self.symbol_table.keys():
            Exception(
                'ERROR', "Conflicting declaration of '{}'".format(ID), tok)

        self.symbol_table[ID] = symbol

    def get_symbol(self, tok: Token, ID: str):
        try:
            return self.symbol_table[ID]
        except KeyError:
            if self.parent is not None:
                return self.parent.get_symbol(tok, ID)
            else:
                Exception(
                    'ERROR', "Unknown identifier '{}'".format(ID), tok)

    def symbols(self, keys: bool = True, values: bool = True
                ) -> Iterator[Union[str, Symbol, Tuple[str, Symbol]]]:
        for k, v in self.symbol_table.items():
            if keys and values:
                yield (k, v)

            elif keys:
                yield k

            elif values:
                yield v
