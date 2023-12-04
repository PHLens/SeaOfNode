from typing_extensions import override
from .node import Node
from myparser import Type Parser

class ConstantNode(Node):
    def __init__(self, type_: Type):
        super().__init__(self, Parser.start)
        self._con = type_

    @override
    def label(self) -> str:
        return "#" + self._con

    @override
    def unique_name(self):
        return f"Con_{self._nid}"

    @override
    def _print1(self, s):
        return self._con._print(s)

    @override
    def compute(self):
        return self._con

    @override
    def idealize(self):
        return None
