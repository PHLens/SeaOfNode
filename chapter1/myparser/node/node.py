class Node():
    _unique_id = 1
    def __init__(self, *args): # node can have zero or multi inputs.
        self._nid = self._unique_id + 1
        self._unique_id += 1
        self._inputs = list(args[1:]) # exclude self.
        self._outputs = []

        for _input in self._inputs:
            if _input is not None:
                _input._outputs.append(self)

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

    @classmethod
    def reset(cls):
        cls._unique_id = 1

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}<0x{id(self)}>"
