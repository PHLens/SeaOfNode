from .type import Type
from typing_extensions import override

class TypeTuple(Type):
    def __init__(self, _types):
        super().__init__(self._tuple)
        self._types = _types

    @override
    def meet(self, other):
        raise NotImplementedError("Meet on Tuple Type not yet implemented")
    
    @override
    def _print(self, s):
        s += "[ "
        for t in self._types:
            s = t._print(s)
            s += ","
        s += "]"
        return s