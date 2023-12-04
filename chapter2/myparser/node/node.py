from abc import abstractmethod
from typing_extensions import override
from .constant_node import ConstantNode
from myparser.type import Type

_unique_id = 1
class Node():
    def __init__(self, *args): # node can have zero or multi inputs.
        global _unique_id
        self._nid = _unique_id + 1
        _unique_id += 1
        self._inputs = list(args[1:]) # exclude self.
        self._outputs = []
        self._type = Type()
        self._disablePeephole = False

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
        return self._print0()

    def _print0(self):
        if self.is_dead():
            return f"{self.unique_name():DEAD}"
        else:
            return self._print1()

    @abstractmethod
    def _print1(self):
        pass

    def In(self, i: int):
        return self._inputs[i]

    def nIns(self) -> int:
        return len(self._inputs)

    def nOuts(self) -> int:
        return len(self._outputs)

    def isUnused(self) -> bool:
        return len(self._outputs) == 0

    def isCFG(self) -> bool:
        return False

    def peephole(self):
        type_ = self._type = self.compute()
        if self._disablePeephole:
            return
        if isinstance(self, ConstantNode) and type_.is_constant():
            self.kill()
            return ConstantNode(type_).peephole()

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
