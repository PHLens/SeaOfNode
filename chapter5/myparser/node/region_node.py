from .node import Node
from myparser.type import CONTROL
from typing_extensions import override

class RegionNode(Node):
    def __init__(self, *inputs):
        super().__init__(*inputs)

    @override
    def label(self) -> str:
        return "Region"
    
    @override
    def _print1(self, s: str):
        return s + self.label() + str(self._nid)
    
    @override
    def isCFG(self) -> bool:
        return True
    
    @override
    def compute(self):
        return CONTROL
    
    @override
    def idealize(self):
        return None