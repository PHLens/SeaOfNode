from .node import Node, ConstantNode
from typing_extensions import override
from myparser.type import Type, TypeInteger, BOTTOM, ZERO

class AddNode(Node):
    def __init__(self, lhs, rhs):
        super().__init__(None, lhs, rhs)

    @override
    def label(self) -> str:
        return "Add"

    @override
    def glabel(self):
        return "+"

    @override
    def _print1(self, s:str) -> str:
        s = self.In(1)._print0(s+"(")
        s = self.In(2)._print0(s+"+")
        return s+")"

    @override
    def compute(self) -> Type:
        i0 = self.In(1)._type
        i1 = self.In(2)._type
        if isinstance(i0, TypeInteger) and isinstance(i1, TypeInteger):
            if i0.is_constant() and i1.is_constant():
                return TypeInteger.constant(i0.value() + i1.value())
            return i0.meet(i1)
        return BOTTOM

    @override
    def idealize(self):
        lhs = self.In(1)
        rhs = self.In(2)
        t1 = lhs._type
        t2 = rhs._type

        # already handled by peephole constant folding
        assert not (t1.is_constant() and t2.is_constant())

        # Add of 0. We do not check for (0+x) because this will already
        # canonicalize to (x+0)
        if isinstance(t2, TypeInteger) and t2.value() == 0:
            return lhs
        
        # Add of same to a multipy by 2
        if lhs == rhs:
            return MulNode(lhs, ConstantNode(TypeInteger.constant(2)).peephole())
        
        # Goal: a left-spine set of adds, with constants on the rhs (which then fold).

        # Move non-adds to RHS
        if not isinstance(lhs, AddNode) and isinstance(rhs, AddNode):
            return self.swap12()
        
        # Now we might see (add add non) or (add non non) or (add add add) but never (add non add)

        # Swap `x+(y+z)` to `(x+y)+z`
        # Rotate (add add add) to remove the add on RHS
        if isinstance(rhs, AddNode):
            return AddNode(AddNode(lhs, rhs.In(1)).peephole(), rhs.In(2))
        
        # Now we might see (add add non) or (add non non) but never (add non add) nor (add add add)
        if not isinstance(lhs, AddNode):
            return self.swap12() if self.spline_cmp(lhs, rhs) else None
        
        # Now we only see (add add non)

        # Replace `(x+con1)+con2` with `x+(con1+con2)`, which then fold the constants.
        if lhs.In(2)._type.is_constant() and t2.is_constant():
            return AddNode(lhs.In(1), AddNode(lhs.In(2), rhs).peephole())

        # Now we sort along the spline via rotates, to gather similar things together.

        # rotate `(x+y)+z` to `(x+z)+y`
        if self.spline_cmp(lhs.In(2), rhs):
            return AddNode(AddNode(lhs.In(1), rhs).peephole(), lhs.In(2))

        return None

    def spline_cmp(self, hi, lo):
        """
            Compare two off-spline nodes and decide what order they should be in.
            Do we rotate ((x + hi) + lo) into ((x + lo) + hi) ?

            Generally constants always go right, then others.
            Ties with in a category sort by node ID.
            `True` if swapping hi and lo.
        """
        if lo._type.is_constant(): return False
        if hi._type.is_constant(): return True

        # Same category of "others"
        return lo._nid > hi._nid

class SubNode(Node):
    def __init__(self, lhs, rhs):
        super().__init__(None, lhs, rhs)

    @override
    def label(self) -> str:
        return "sub"

    @override
    def glabel(self):
        return "-"

    @override
    def _print1(self, s: str):
        s = self.In(1)._print0(s + "(")
        s = self.In(2)._print0(s + "-")
        s += ")"
        return s

    @override
    def compute(self) -> Type:
        i0 = self.In(1)._type
        i1 = self.In(2)._type
        if isinstance(i0, TypeInteger) and isinstance(i1, TypeInteger):
            if i0.is_constant() and i1.is_constant():
                return TypeInteger.constant(i0.value() - i1.value())
            return i0.meet(i1)
        return BOTTOM

    @override
    def idealize(self):
        return None

class MinusNode(Node):
    def __init__(self, input_):
        super().__init__(None, input_)

    @override
    def label(self) -> str:
        return "Minus"

    @override
    def glabel(self):
        return "-"

    @override
    def _print1(self, s:str) -> str:
        s = self.In(1)._print0(s+"(-")
        return s+")"

    @override
    def compute(self) -> Type:
        i0 = self.In(1)._type
        if isinstance(i0, TypeInteger):
            return TypeInteger.constant(-i0.value()) if i0.is_constant() else i0
        return BOTTOM

    @override
    def idealize(self):
        return None

class MulNode(Node):
    def __init__(self, lhs, rhs):
        super().__init__(None, lhs, rhs)

    @override
    def label(self) -> str:
        return "Mul"

    @override
    def glabel(self):
        return "*"

    @override
    def _print1(self, s:str) -> str:
        s = self.In(1)._print0(s+"(")
        s = self.In(2)._print0(s+"*")
        return s+")"

    @override
    def compute(self) -> Type:
        i0 = self.In(1)._type
        i1 = self.In(2)._type
        if isinstance(i0, TypeInteger) and isinstance(i1, TypeInteger):
            if i0.is_constant() and i1.is_constant():
                return TypeInteger.constant(i0.value() * i1.value())
            return i0.meet(i1)
        return BOTTOM

    @override
    def idealize(self):
        lhs = self.In(1)
        rhs = self.In(2)
        t1 = lhs._type
        t2 = rhs._type

        # Mul of 1. We do not check for (1*x) because this will already
        # canonicalize to (x*1)
        if (t2.is_constant() and isinstance(t2, TypeInteger) and t2.value() == 1):
            return lhs
        
        # Move constants to RHS: con*arg becomes arg*con
        if t1.is_constant() and not t2.is_constant():
            return self.swap12()

        return None

class DivNode(Node):
    def __init__(self, lhs, rhs):
        super().__init__(None, lhs, rhs)

    @override
    def label(self) -> str:
        return "Div"

    @override
    def glabel(self):
        return "//"

    @override
    def _print1(self, s:str) -> str:
        s = self.In(1)._print0(s+"(")
        s = self.In(2)._print0(s+"/")
        return s+")"

    @override
    def compute(self) -> Type:
        i0 = self.In(1)._type
        i1 = self.In(2)._type
        if isinstance(i0, TypeInteger) and isinstance(i1, TypeInteger):
            if i0.is_constant() and i1.is_constant():
                return TypeInteger.constant(i0.value() // i1.value()) if i1.value() != 0 else ZERO
            return i0.meet(i1)
        return BOTTOM

    @override
    def idealize(self):
        return None

class NotNode(Node):
    def __init__(self, in_):
        super().__init__(None, in_)

    @override
    def label(self) -> str:
        return "Not"

    @override
    def glabel(self):
        return "!"

    @override
    def _print1(self, s: str):
        s = self.In(1)._print0(s + "(!")
        return s + ")"
    
    @override
    def compute(self):
        i0 = self.In(1)._type
        if isinstance(i0, TypeInteger):
            return TypeInteger.constant(1 if i0.value()==0 else 0) if i0.is_constant() else i0
        return BOTTOM
    
    @override
    def idealize(self):
        return None