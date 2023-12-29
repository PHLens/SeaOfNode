from .node import Node, ConstantNode
from typing_extensions import override
from abc import abstractmethod
from myparser.type import TypeInteger, BOTTOM

class BoolNode(Node):
    def __init__(self, lhs, rhs):
        super().__init__(None, lhs, rhs)
    
    @abstractmethod
    def op(self) ->str:
        pass

    @override
    def label(self):
        return self.__class__.__name__
    
    @override
    def glabel(self):
        return self.op()
    
    @override
    def _print1(self, s: str):
        s = self.In(1)._print0(s + "(")
        s = self.In(2)._print0(s + self.op())
        s += ")"
        return s
    
    @override
    def compute(self):
        i0 = self.In(1)._type
        i1 = self.In(2)._type
        if isinstance(i0, TypeInteger) and isinstance(i1, TypeInteger):
            if i0.is_constant() and i1.is_constant():
                return TypeInteger.constant(1 if self.doOp(i0.value(), i1.value()) else 0)
            return i0.meet(i1)
        return BOTTOM
    
    @abstractmethod
    def doOp(self, lhs, rhs):
        pass

    @override
    def idealize(self):
        # compare of same
        if self.In(1) == self.In(2):
            return ConstantNode(TypeInteger.constant(1 if self.doOp(3, 3) else 0))
        
        return None
    
class EQ(BoolNode):
    def __init__(self, lhs, rhs):
        super().__init__(lhs, rhs)

    @override
    def op(self):
        return "=="
    
    @override
    def doOp(self, lhs, rhs):
        return lhs == rhs
    

class LT(BoolNode):
    def __init__(self, lhs, rhs):
        super().__init__(lhs, rhs)

    @override
    def op(self):
        return "<"
    
    @override
    def doOp(self, lhs, rhs):
        return lhs < rhs
    

class LE(BoolNode):
    def __init__(self, lhs, rhs):
        super().__init__(lhs, rhs)

    @override
    def op(self):
        return "<="
    
    @override
    def doOp(self, lhs, rhs):
        return lhs <= rhs