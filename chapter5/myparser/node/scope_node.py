from .node import Node
from .region_node import RegionNode
from .phi_node import PhiNode
from typing_extensions import override
from myparser.type import BOTTOM

class ScopeNode(Node):
    """
        The Scope node is purely a parser helper
        - it tracks names to nodes with a stack of scopes.
    """
    CTRL = "$ctrl"
    ARG0 = "arg"
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

    def ctrl(self):
        return self.In(0)
    
    def ctrln(self, n):
        """
            The ctrl of a ScopeNode is always bound to the currently active
            control node in the graph, via a special name '$ctrl' that is not
            a valid identifier in the language grammar and hence cannot be
            referenced in Simple code.

            @param n The node to be bound to '$ctrl'

            @return Node that was bound
        """
        return self.set_def(0, n)
    
    def dup(self):
        """
            Duplicate a ScopeNode; including all levels, up to Nodes.  So this is
            neither shallow (would dup the Scope but not the internal HashMap
            tables), nor deep (would dup the Scope, the HashMap tables, but then
            also the program Nodes).
            
            The new Scope is a full-fledged Node with proper use<->def edges.
        """
        dup = ScopeNode()
        # Our goals are:
        # 1) duplicate the name bindings of the ScopeNode across all stack levels
        # 2) Make the new ScopeNode a user of all the nodes bound
        # 3) Ensure that the order of defs is the same to allow easy merging
        for syms in self._scopes:
            dup._scopes.append(syms)
        dup.add_def(self.ctrl())
        for i in range(1, self.nIns()):
            dup.add_def(self.In(i))
        return dup
    
    def merge_scopes(self, that):
        """
            Merges the names whose node bindings differ, by creating Phi node for such names
            The names could occur at all stack levels, but a given name can only differ in the
            innermost stack level where the name is bound.

            @param that The ScopeNode to be merged into this
            @return A new node representing the merge point
        """
        r = self.ctrln(RegionNode(None, self.ctrl(), that.ctrl()).peephole())
        ns = self.reverse_names()
        # Note that we skip i==0, which is bound to '$ctrl'
        for i in range(1, self.nIns()):
            if self.In(i) != that.In(i): # No need for redundant Phis
                self.set_def(i, PhiNode(ns[i], r, self.In(i), that.In(i)).peephole())
        that.kill()   # kill merged scope
        return r