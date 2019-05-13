from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Tuple

import llvmlite.ir as ir

from src.structs.Symbols import SymbolTable

if TYPE_CHECKING:
    from src.structs.Block import Block
    from src.structs.Type import WappaType


class Function:
    def __init__(self, ID: str,
                 modifiers: Tuple[bool, bool, Optional[str], Optional[str]],
                 parameters: List[Tuple[str, WappaType]],
                 ret_type: Optional[WappaType], block: Block):
        self.scope = block.scope
        self.ID = ID
        self.parameters = parameters
        self.ret_type = ret_type
        self.block = block

        self.compiled = False

    def inline(self, args: List[str]) -> str:
        return ""

    def compile(self, module: ir.Module, builder: ir.IRBuilder,
                symbols: SymbolTable) -> ir.Value:
        if not self.compiled:
            self.compiled = True

            self.func_type = ir.FunctionType(self.ret_type.ir_type, [
                p[1].ir_type for p in self.parameters])

            self.func = ir.Function(module, self.func_type, name=self.ID)

            symbols = SymbolTable(parent=symbols)

            for i, p in enumerate(self.parameters):
                self.func.args[i].name = p[0]

                symbols.add_symbol(p[0], self.func.args[i])

            block = self.func.append_basic_block('entry')

            builder = ir.IRBuilder(block)

            self.block.compile(module, builder, symbols)

            return self.func
        else:
            return self.func


class NativeFunction(Function):
    def __init__(self, ID, parameters: List[Tuple[str, WappaType]],
                 ret_type: Optional[WappaType]):
        self.ID = ID
        self.parameters = parameters
        self.ret_type = ret_type

    def inline(self, args: List[str]) -> str:
        return ""

    def compile(self, module: ir.Module, builder: ir.IRBuilder,
                symbols: SymbolTable) -> ir.Value:
        return ""
