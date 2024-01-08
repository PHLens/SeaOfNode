from .node import MultiNode
from myparser.type import IF
from typing_extensions import override

class IfNode(MultiNode):
    def __init__(self, ctrl, pred):
        super().__init__(ctrl, pred)

    @override
    def label(self):
        return "If"

    @override
    def _print1(self, s):
        s += "if( "
        s = self.In(1)._print0(s)
        return s + " )"

    @override
    def isCFG(self):
        return True
    
    def ctrl(self):
        return self.In(0)
    
    def pred(self):
        return self.In(1)

    @override
    def compute(self):
        return IF
    
    @override
    def idealize(self):
        return None