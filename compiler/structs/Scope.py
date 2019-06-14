from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union

import llvmlite.ir as ir

from gen.Wappa import Token

from ..util import WappaException

if TYPE_CHECKING:
    from .Field import Field
    from .Function import Function
    from .Type import WappaType
    from .Variable import Variable

    Symbol = Union[WappaType, Field, Function, Variable]


class Scope:
    def __init__(self, module: ir.Module, parent: Scope = None):
        self.owner: Optional[Symbol] = None
        self.module = module
        self.parent = parent
        self.symbol_table: Dict[str, Symbol] = {}

    def add_symbol(self, tok: Token, ID: str, symbol: Symbol):
        if ID in self.symbol_table.keys():
            WappaException(
                'ERROR', "Conflicting declaration of '{}'".format(ID), tok)

        self.symbol_table[ID] = symbol

    def get_symbol(self, tok: Token, ID: str, WappaException: bool = True
                   ) -> Optional[Symbol]:
        try:
            return self.symbol_table[ID]
        except KeyError:
            if self.parent is not None:
                return self.parent.get_symbol(tok, ID)
            else:
                if WappaException:
                    WappaException(
                        'ERROR', "Unknown identifier '{}'".format(ID), tok)
                return None

    def symbols(self, keys: bool = False, values: bool = False
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
