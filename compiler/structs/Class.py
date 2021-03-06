from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Tuple

import llvmlite.ir as ir

from gen.Wappa import Token

from .Field import Field
from .Symbols import SymbolTable
from .Type import WappaType

if TYPE_CHECKING:
    from .Interface import Interface
    from .Scope import Scope, Symbol


class Class(WappaType):
    def __init__(
        self, scope: Scope, ID: str, parent: Class,
        interfaces: List[Interface],
        modifiers: Tuple[Optional[str], Optional[str]]
    ):
        self.interfaces = interfaces.copy()
        interfaces.append(parent)

        WappaType.__init__(self, ID, supertypes=interfaces)

        self.scope = scope
        scope.owner = self
        self.parent = parent
        self.modifiers = modifiers

    def get_symbol(self, tok: Token, ID: str) -> Symbol:
        ret = self.scope.get_symbol(tok, ID, not self.parent)

        if not ret and self.parent:
            return self.parent.get_symbol(tok, ID)

        return ret

    @property
    def ir_type(self):
        if self._ir_type:
            return self._ir_type

        self._ir_type = self.scope.module.context.get_identified_type(self.ID)

        field_types = []
        self.field_names = []
        for f in self.scope.symbols(values=True):
            if isinstance(f, Field):
                self.field_names.append(f.ID)
                field_types.append(f.ir_type)

        self._ir_type.set_body(*field_types)

        return self._ir_type

    @ir_type.setter
    def ir_type(self, value):
        self._ir_type = value

    def compile(self, module: ir.Module, builder: ir.IRBuilder,
                symbols: SymbolTable) -> ir.Value:
        # if self.parent:
        #     ID = "{} : {}".format(ID, self.parent.ID)

        # modifiers = filter(lambda x: x is not None, self.modifiers)

        members = self.scope.symbols(values=True)

        fields: List[Field] = []
        methods: List[Function] = []

        for s in members:
            if isinstance(s, Field):
                fields.append(s)

            elif isinstance(s, Function):
                methods.append(s)

        symbols.add_symbol(self.ID, self.ir_type, self.field_names)
        symbols = SymbolTable(parent=symbols)

        for f in fields:
            symbols.add_symbol(f.ID, f.compile(
                module, builder, symbols))

        for m in methods:
            m.compile(module, builder, symbols)


if True:
    from .Function import Function
