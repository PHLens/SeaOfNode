class Type:
    _bot = bytes(0) # Bottom (ALL)
    _top = bytes(1) # Top    (ANY)
    _simple = bytes(2) # End of _simple Types
    _int = bytes(3)  # All Integers
    strs = ["BOTTOM", "TOP"]
    def __init__(self, type_):
        self._type = type_

    def is_simple(self):
        return self._type < Type._simple

    def is_constant(self):
        return self._type == Type._top

    def _print(self, s):
        return s.append(Type.strs[self._type]) if self.is_simple() else s

BOTTOM = Type(Type._bot)
