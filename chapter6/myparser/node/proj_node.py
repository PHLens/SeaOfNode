from myparser.node import Node, MultiNode, IfNode
from typing_extensions import override
from myparser.type import TypeTuple, BOTTOM

class ProjNode(Node):
    def __init__(self, ctrl, idx, label):
        super().__init__(ctrl)
        self._idx = idx
        self._label = label

    @override
    def label(self):
        return self._label

    @override
    def _print1(self, s: str):
        return s + self._label

    @override
    def isCFG(self) -> bool:
        return self._idx == 0 or isinstance(self.ctrl(), IfNode)
    
    def ctrl(self) -> MultiNode:
        return self.In(0)

    @override
    def compute(self):
        t = self.ctrl()._type
        return t._types[self._idx] if isinstance(t, TypeTuple) else BOTTOM

    @override
    def idealize(self):
        return None