class Type:
    _bot = bytes(0) # Bottom (ALL)
    _top = bytes(1) # Top    (ANY)
    _simple = bytes(2) # End of _simple Types
    _int = bytes(3)  # All Integers

    def __init__(self, type_):
        self._type = type_
        self.strs = ["BOTTOM", "TOP"]
        self.bottom = Type(self._bot)

    def is_simple(self):
        return self._type < self._simple

    def is_constant(self):
        return self._type == self._top

    def _print(self, s):
        return s.append(self.strs[self._type]) if self.is_simple() else s
