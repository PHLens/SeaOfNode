from abc import abstractmethod
from typing_extensions import override
from myparser.type import Type, BOTTOM
from myparser.utils import BitVector

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

    def __repr__(self):
        return self.print()

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
        """
            Change a `def` into a Node.
            Keeps the edges correct, by removing the corresponding `ues-def` edge.
            This may make original `def` go dead.

            @param idx which def to set
            @param new_def the new definition
            @return new_def for flow coding
        """
        old_def = self.In(idx)
        if old_def is new_def:
            return self # No change
        # add new_def to the corresponding `def-use` edge
        # This needs to happen before removing old node's `def-use` edge as
        # the new_def might get killed if the old node kills it recursively.
        if new_def is not None:
            new_def.add_use(self)
        if old_def is not None and old_def.del_use(self):# remove the last element of old_def, now old_def is DEAD.
            old_def.kill()
        self._inputs[idx] = new_def
        return new_def

    def add_def(self, new_def):
        """
            add a new def to an existing Node.
            Keep the edges correct by adding the corresponding `def-use` edge.

            @param new_def the new definition, appended to the end of existing definitions
            @return new_def for flow coding
        """
        self._inputs.append(new_def)
        if new_def is not None:
            new_def.add_use(self)
        return new_def

    def add_use(self, n):
        self._outputs.append(n)
        return n

    def del_use(self, use):
        if use in self._outputs:
            self._outputs[self._outputs.index(use)] = self._outputs[-1] # set last ele into `use` position, so last ele can be removed.
            self._outputs.pop()
        return len(self._outputs) == 0

    def popN(self, n: int):
        for i in range(n):
            old_def = self._inputs.pop()
            if old_def is not None and old_def.del_use(self):
                old_def.kill()

    def kill(self):
        assert(self.isUnused())
        self.popN(self.nIns())
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
        cls._disablePeephole = False

    def find(self, nid:int):
        """
            Debugging utility to find a Node by index.
        """
        return self._find(BitVector(), nid)

    def _find(self, visit: BitVector, nid: int):
        if self._nid == nid:
            return self
        if visit.get(self._nid):
            return None
        visit.set(self._nid)
        for def_ in self._inputs:
            if def_ is not None:
                rez = def_._find(visit, nid)
                if rez is not None:
                    return rez
        for use in self._outputs:
            rez = use._find(visit, nid)
            if rez is not None:
                return rez
        return None
    

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