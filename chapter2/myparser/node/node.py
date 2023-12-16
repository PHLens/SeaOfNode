from abc import abstractmethod
from typing_extensions import override
from myparser.type import Type, TypeInteger, BOTTOM

class Node():
    _unique_id = 1
    _disablePeephole = False
    def __init__(self, *args): # node can have zero or multi inputs.
        self._nid = Node._unique_id
        Node._unique_id += 1
        self._inputs = list(args)
        self._outputs = []
        self._type = None

        for _input in self._inputs:
            if _input is not None:
                _input._outputs.append(self)
    def label(self) -> str:
        pass

    def unique_name(self):
        return self.label() + str(self._nid)

    def glabel(self):
        return self.label()

    def print(self):
        return self._print0("")

    def _print0(self, s:str):
        if self.is_dead():
            return f"{self.unique_name():DEAD}"
        else:
            return self._print1(s)

    @abstractmethod
    def _print1(self, s:str):
        pass

    def In(self, i: int):
        return self._inputs[i]

    def nIns(self) -> int:
        return len(self._inputs)

    def out(self, i: int):
        return self._outputs[i]

    def nOuts(self) -> int:
        return len(self._outputs)

    def isUnused(self) -> bool:
        return self.nOuts() == 0

    def isCFG(self) -> bool:
        return False

    def peephole(self):
        type_ = self._type = self.compute()
        if Node._disablePeephole:
            return self
        if not isinstance(self, ConstantNode) and type_.is_constant():
            self.kill()
            return ConstantNode(type_).peephole()
        n = self.idealize()
        if n is not None:
            return n
        return self

    def set_def(self, idx: int, new_def):
        old_def = self.In(idx)
        if old_def is self:
            return
        if new_def is not None:
            new_def._outputs.append(self)
        if old_def is not None:
            outs = old_def._outputs
            last_idx = len(outs) - 1
            outs[outs.index(self)] = outs[last_idx] # set last ele into self position, so last ele can be removed.
            outs.pop(last_idx)
            if last_idx == 0: # remove the last element of old_def, now old_def is DEAD.
                old_def.kill()
        self._inputs[idx] = new_def

    def kill(self):
        assert(self.isUnused())
        for i in range(self.nIns()):
            self.set_def(i, None)
        self._inputs.clear()
        self._type = None
        assert(self.is_dead())

    def is_dead(self):
        return self.isUnused() and self.nIns() == 0 and self._type == None

    @abstractmethod
    def compute(self):
        pass

    @abstractmethod
    def idealize(self):
        pass

    @classmethod
    def reset(cls):
        cls._unique_id = 1

    def __repr__(self):
        return self.print()

class ConstantNode(Node):
    def __init__(self, type_: Type):
        from ..parser import Parser
        super().__init__(Parser.START)
        self._con = type_

    @override
    def label(self) -> str:
        return f"#{self._con}"

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

class StartNode(Node):
    def __init__(self):
        super().__init__()

    @override
    def label(self) -> str:
        return "Start"

    @override
    def _print1(self, s: str):
        return s + self.label()

    def isCFG(self) -> bool:
        return True;

    @override
    def compute(self):
        return BOTTOM

    @override
    def idealize(self):
        return None

class ReturnNode(Node):
    def __init__(self, ctrl, data):
        super().__init__(ctrl, data)

    def ctrl(self) -> Node:
        return self.In(0)

    def expr(self) -> Node:
        return self.In(1)

    @override
    def label(self) -> str:
        return "Return"

    @override
    def _print1(self, s: str):
        return self.expr()._print0(s + "return ") + ";"

    def isCFG(self) -> bool:
        return True;

    @override
    def compute(self):
        return BOTTOM

    @override
    def idealize(self):
        return None

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
        return None;
