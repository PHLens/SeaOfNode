from .node import Node
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
        return BOTTOM

    @override
    def idealize(self):
        # TODO: add of 0.
        return None;

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
        self.In(1)._print0(s + "(")
        self.In(2)._print0(s + "-")
        s += ")"
        return s

    @override
    def compute(self) -> Type:
        i0 = self.In(1)._type
        i1 = self.In(2)._type
        if isinstance(i0, TypeInteger) and isinstance(i1, TypeInteger):
            if i0.is_constant() and i1.is_constant():
                return TypeInteger.constant(i0.value() - i1.value())
        return BOTTOM

    @override
    def idealize(self):
        return None;

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
        return None;

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
        return BOTTOM

    @override
    def idealize(self):
        return None;

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
        return BOTTOM

    @override
    def idealize(self):
        return None