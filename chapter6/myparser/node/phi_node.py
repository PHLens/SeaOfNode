from .node import Node
from myparser.type import BOTTOM
from typing_extensions import override

class PhiNode(Node):
    def __init__(self, label:str, *inputs):
        super().__init__(*inputs)
        self._label = label

    @override
    def label(self):
        return "Phi_" + self._label

    @override
    def glabel(self):
        return "&phi;_" + self._label

    @override
    def _print1(self, s):
        s += "Phi("
        for node in self._inputs:
            s = node._print0(s)
            s += ","
        s = s[:-1] # exculde last ','
        s += ")"
        return s

    def region(self):
        return self.In(0)

    @override
    def compute(self):
        return BOTTOM

    @override
    def idealize(self):
        # remove a "junk" Phi: Phi(x,x) is just x
        if self.same_inputs():
            return self.In(1)
        
        # Phi(op(A,B),op(Q,R),op(X,Y)) becomes
        #   op(Phi(A,Q,X), Phi(B,R,Y)).
        # Less op, more Phi, but Phis do not make code.
        op = self.In(1)
        if op.nIns() == 3 and op.In(0) == None and not op.isCFG() and self.same_op():
            lhss = [Node() for i in range(self.nIns())]
            rhss = [Node() for i in range(self.nIns())]
            lhss[0] = rhss[0] = self.In(0) # set Region
            for i in range(1, self.nIns()):
                lhss[i] = self.In(i).In(1)
                rhss[i] = self.In(i).In(2)
            phi_lhs = PhiNode(self._label, *lhss).peephole()
            phi_rhs = PhiNode(self._label, *rhss).peephole()
            return op.copy(phi_lhs, phi_rhs)
        return None
    
    def same_op(self):
        for i in range(2, self.nIns()):
            if self.In(1).__class__ != self.In(i).__class__:
                return False
        return True
    
    def same_inputs(self):
        for i in range(2, self.nIns()):
            if self.In(1) != self.In(i):
                return False
        return True