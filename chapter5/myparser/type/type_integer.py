from .type import Type
from typing_extensions import override

class TypeInteger(Type):
    def __init__(self, is_con, con):
        super().__init__(self._int)
        self._is_con = is_con
        self._con = con

    @classmethod
    def constant(cls, con):
        return TypeInteger(True, con)
    
    def is_top(self):
        return (not self._is_con and self._con == 0)
    
    def is_bot(self):
        return (not self._is_con and self._con == 1)

    @override
    def _print(self, s):
        if self.is_top(): return s + "IntTop"
        if self.is_bot(): return s + "IntBot"
        return s + f"{self._con}"

    @override
    def is_constant(self):
        return self._is_con

    def value(self):
        return self._con

    @override
    def meet(self, other):
        if self is other: return self
        if not isinstance(other, TypeInteger): return super.meet(other)
        # BOT wins
        if self.is_bot(): return self
        if other.is_bot(): return other
        # TOP loses
        if other.is_top(): return self
        if self.is_top(): return other
        assert self.is_constant() and other.is_constant()
        return self if self._con == 1 else BOT

    @override
    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, TypeInteger):
            return False
        return self._con == other._con and self._is_con == other._is_con

    @override
    def __repr__(self) -> str:
        return self._print("")

TOP = TypeInteger(False, 0)
BOT = TypeInteger(False, 1)
ZERO = TypeInteger(True, 0)