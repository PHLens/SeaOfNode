class Type:
    """
        These types are part of a Monotone Analysis Framework,
        see <a href="https://www.cse.psu.edu/~gxt29/teaching/cse597s21/slides/08monotoneFramework.pdf">see for example this set of slides</a>.
        
        The types form a lattice; @see <a href="https://en.wikipedia.org/wiki/Lattice_(order)">a symmetric complete bounded (ranked) lattice.</a>
       
        This wild lattice theory will be needed later to allow us to easily beef up
        the analysis and optimization of the Simple compiler... but we don't need it
        now, just know that it is coming along in a later Chapter.
        
        One of the fun things here is that while the theory is deep and subtle, the
        actual implementation is darn near trivial and is generally really obvious
        what we're doing with it.  Right now, it's just simple integer math to do
        simple constant folding e.g. 1+2 == 3 stuff.
    """
    # --------------------------------------------
    # Simple types are implemented fully here. `Simple` means: the code and
    # type hierarchy are simple, not that the Type is conceptually simple.
    _bot = bytes(0) # Bottom (ALL)
    _top = bytes(1) # Top    (ANY)
    _ctrl = bytes(2) # Ctrl flow bottom
    _simple = bytes(3) # End of _simple Types
    _int = bytes(4)  # All Integers
    _tuple = bytes(5) # Tuplesl finite collections of unrelated Types. kept in parallel

    strs = ["Bot", "Top", "Ctrl"]
    def __init__(self, type_):
        self._type = type_

    def is_simple(self):
        return self._type < Type._simple

    def is_constant(self):
        return self._type == Type._top

    def _print(self, s):
        return s.append(Type.strs[self._type]) if self.is_simple() else s
    
    def meet(self, other):
        return BOTTOM
    
    def __repr__(self) -> str:
        return self._print("")

BOTTOM = Type(Type._bot)  # ALL
TOP = Type(Type._top)  # ANY
CONTROL = Type(Type._ctrl)  # Ctrl
