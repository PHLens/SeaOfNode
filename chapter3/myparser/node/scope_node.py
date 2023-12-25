from .node import Node
from typing_extensions import override
from myparser.type import BOTTOM

class ScopeNode(Node):
    """
        The Scope node is purely a parser helper
        - it tracks names to nodes with a stack of scopes.
    """
    def __init__(self):
        super().__init__()
        self._scopes = []
        self._type = BOTTOM

    @override
    def label(self) -> str:
        return "Scope"
    
    @override
    def _print1(self, s: str):
        s += self.label()
        for scope in self._scopes:
            s += "["
            first = True
            for name in scope.keys():
                if not first:
                    s += ", "
                first = False
                s += f"{name}:"
                n = self.In(scope.get(name))
                if n is None:
                    s += "null"
                else:
                    s = n._print0(s)
                s += "]"
        return s

    def reverse_names(self):
        names = []
        for syms in self._scopes:
            for name in syms.keys():
                names.insert(syms.get(name), name)
        return names
    
    @override
    def compute(self):
        return BOTTOM
    
    @override
    def idealize(self):
        return None
    
    def push(self):
        self._scopes.append({})

    def pop(self):
        self.popN(len(self._scopes.pop()))

    def define(self, name, n: Node):
        """
            create a new name in current scope.
        """
        syms = self._scopes[-1]
        if name in syms: # double define, no need to add def
            syms[name] = self.nIns()
            return None
        syms[name] = self.nIns()
        return self.add_def(n)

    def lookup(self, name):
        """
            lookup a name in all scopes starting from most deeply nested.

            @param name Name to be looked up
        """
        return self.update(name, None, len(self._scopes)-1)

    def update(self, name, node:Node, nestingLevel=None):
        """
            Both recursive lookup and update.
            A shared implementation allows us to create lazy phis both during
            lookups and updates; the lazy phi creation is part of chapter 8.
        """
        if nestingLevel == None:
            nestingLevel = len(self._scopes) - 1
        if nestingLevel < 0: # no scopes found.
            return None
        syms = self._scopes[nestingLevel]
        if name not in syms: # not found in this scope, recursively look up
            return self.update(name, node, nestingLevel-1)
        idx = syms.get(name)
        old = self.In(idx)
        # if node is None, we are doing lookup rather than update, hence return existing value
        return old if node == None else self.set_def(idx, node)

    def crtl(self):
        return self.In(0)
    
    def crtl(self, n: Node):
        return self.set_def(0, n)