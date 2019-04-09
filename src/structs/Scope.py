from __future__ import annotations

from typing import Dict, List, Tuple, Union

from src.gen.Wappa import Token
from src.structs import Class, Field, Function
from src.util import Exception

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
                ) -> List[Union[str, Symbol, Tuple[str, Symbol]]]:
        ret = []
        for k, v in self.symbol_table.items():
            if keys and values:
                ret.append((k, v))

            elif keys:
                ret.append(k)  # type: ignore

            elif values:
                ret.append(v)

        return ret  # type: ignore
