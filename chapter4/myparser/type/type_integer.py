from .type import Type
from typing_extensions import override

class TypeInteger(Type):
    def __init__(self, con):
        super().__init__(self._int)
        self._con = con

    @classmethod
    def constant(cls, con):
        return TypeInteger(con)

    @override
    def _print(self, s):
        return s + f"{self._con}"

    @override
    def is_constant(self):
        return True

    def value(self):
        return self._con

    @override
    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, TypeInteger):
            return False
        return self._con == other._con

    @override
    def __repr__(self) -> str:
        return self._print("")

ZERO = TypeInteger(0)
