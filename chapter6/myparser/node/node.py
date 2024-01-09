from abc import abstractmethod
from typing_extensions import override
from myparser.type import Type, TypeTuple, BOTTOM
from myparser.utils import BitVector

class Node():
    _unique_id = 1
    _disablePeephole = False # allow disabling peephole so that we can observe the full graph.
    def __init__(self, *args): # node can have zero or multi inputs.
        self._nid = Node._unique_id
        Node._unique_id += 1
        self._inputs = list(args)
        self._outputs = []
        self._type = None

        for _input in self._inputs:
            if _input is not None:
                _input.add_use(self)
    def label(self) -> str:
        pass

    def unique_name(self):
        return self.label() + str(self._nid)

    def glabel(self):
        return self.label()

    def __repr__(self):
        return self.print()

    def print(self):
        return self._print0("")

    def _print0(self, s:str):
        if self.is_dead():
            return f"{self.unique_name():DEAD}"
        else:
            return self._print1(s)

    @abstractmethod
    def _print1(self, s:str):
        pass

    def In(self, i: int):
        return self._inputs[i]

    def nIns(self) -> int:
        return len(self._inputs)

    def out(self, i: int):
        return self._outputs[i]

    def nOuts(self) -> int:
        return len(self._outputs)

    def isUnused(self) -> bool:
        return self.nOuts() == 0

    def isCFG(self) -> bool:
        return False

    def set_def(self, idx: int, new_def):
        """
            Change a `def` into a Node.
            Keeps the edges correct, by removing the corresponding `ues-def` edge.
            This may make original `def` go dead.

            @param idx which def to set
            @param new_def the new definition
            @return new_def for flow coding
        """
        old_def = self.In(idx)
        if old_def is new_def:
            return self # No change
        # add new_def to the corresponding `def-use` edge
        # This needs to happen before removing old node's `def-use` edge as
        # the new_def might get killed if the old node kills it recursively.
        if new_def is not None:
            new_def.add_use(self)
        if old_def is not None and old_def.del_use(self):# remove the last element of old_def, now old_def is DEAD.
            old_def.kill()
        self._inputs[idx] = new_def
        return new_def

    def add_def(self, new_def):
        """
            add a new def to an existing Node.
            Keep the edges correct by adding the corresponding `def-use` edge.

            @param new_def the new definition, appended to the end of existing definitions
            @return new_def for flow coding
        """
        self._inputs.append(new_def)
        if new_def is not None:
            new_def.add_use(self)
        return new_def

    def add_use(self, n):
        self._outputs.append(n)
        return n

    def del_use(self, use):
        if use in self._outputs:
            self._outputs[self._outputs.index(use)] = self._outputs[-1] # set last ele into `use` position, so last ele can be removed.
            self._outputs.pop()
        return len(self._outputs) == 0

    def popN(self, n: int):
        for i in range(n):
            old_def = self._inputs.pop()
            if old_def is not None and old_def.del_use(self):
                old_def.kill()

    def kill(self):
        assert(self.isUnused())
        self.popN(self.nIns())
        self._type = None
        assert(self.is_dead())

    def is_dead(self):
        return self.isUnused() and self.nIns() == 0 and self._type == None

    def keep(self):
        """
            Add bogus null use to keep node alive.
            Shortcuts to stop DCE(Dead Code Elimination) mid-parse.
        """
        return self.add_use(None)
    
    def unkeep(self):
        """
            Remove bogus null.
        """
        self.del_use(None)
        return self
    
    # --------------------------------------
    # Graph-based optimizations
    def peephole(self):
        # compute initial or improved Type
        type_ = self._type = self.compute()

        if Node._disablePeephole: # without peephole
            return self
        
        # Replace constant computations from non-constants with a constant node
        if not isinstance(self, ConstantNode) and type_.is_constant():
            return self.deadCodeElim(ConstantNode(type_).peephole())
        
        # Future chapter: Global Value Numbering

        # Ask each node for a better replacement
        n = self.idealize()
        if n is not None:  # something changed
            # Recursively optimize
            return self.deadCodeElim(n.peephole())
        return self        # No progress

    def deadCodeElim(self, m):
        """
            m is the new Node, self is the old.
            Return 'm', which may have zero use but is alive nonetheless.
            If self has zero use (and is not 'm'), kill self.
        """
        if m is not self and self.isUnused():
            # Killing self - and this may recursively kill self's inputs
            # which might end up killing m, so we add a bogus extra null output
            # edge to stop kill().
            m.keep()
            self.kill()
            m.unkeep()
        return m

    @abstractmethod
    def compute(self):
        """
            This function needs to be
            <a href="https://en.wikipedia.org/wiki/Monotonic_function">Monotonic</a>
            as it is part of a Monotone Analysis Framework.
            <a href="https://www.cse.psu.edu/~gxt29/teaching/cse597s21/slides/08monotoneFramework.pdf">See for example this set of slides</a>.
            
            For Chapter 2, all our Types are really integer constants, and so all
            the needed properties are trivially true, and we can ignore the high
            theory.  Much later on, this will become important and allow us to do
            many fancy complex optimizations trivially... because theory.
            
            compute() needs to be stand-alone, and cannot recursively call compute
            on its inputs programs are cyclic (have loops!) and this will just
            infinitely recurse until stack overflow.  Instead, compute typically
            computes a new type from the `_type` field of its inputs.
        """
        pass

    @abstractmethod
    def idealize(self):
        """
            This function rewrites the current Node into a more "idealized" form.
            This is the bulk of our peephole rewrite rules, and we use this to
            e.g. turn arbitrary collections of adds and multiplies with mixed
            constants into a normal form that's easy for hardware to implement.
            Example: An array addressing expression:
                ary[idx+1]
            might turn into Sea-of-Nodes IR:
                (ary+12)+((idx+1) * 4)
            This expression can then be idealized into:
                ary + ((idx*4) + (12 + (1*4)))
            And more folding:
                ary + ((idx<<2) + 16)
            And during code-gen:
                MOV4 Rary,Ridx,16 // or some such hardware-specific notation
            
            `idealize` has a very specific calling convention:
            - If NO change is made, return `null`
            - If ANY change is made, return not-null; this can be `self`
            - The returned Node does NOT call `peephole` on itself; the `peephole` call will recursively peephole it.
            - Any NEW nodes that are not directly returned DO call `peephole`.

            Since idealize calls peephole and peephole calls idealize, you must be
            careful that all idealizations are *monotonic*: all transforms remove
            some feature, so that the set of available transforms always shrinks.
            If you don't, you risk an infinite peephole loop!
            
            @return Either a new or changed node, or null for no changes.
        """
        pass

    # ------------------------------
    # Peephole utilities

    # swap inputs without letting either input go dead during the swap.
    def swap12(self):
        tmp = self.In(1)
        self._inputs[1] = self.In(2)
        self._inputs[2] = tmp
        return self

    def allCons(self):
        """
            does this node contain all constants?
            Ignore In(0), as is usually control
        """
        for i in range(1, self.nIns()):
            if not self.In(i)._type.is_constant():
                return False
        return True

    def copy(self, lhs, rhs):
        raise NotImplementedError("Binary ops need to implement copy")

    @classmethod
    def reset(cls):
        cls._unique_id = 1
        cls._disablePeephole = False

    def find(self, nid:int):
        """
            Debugging utility to find a Node by index.
        """
        return self._find(BitVector(), nid)

    def _find(self, visit: BitVector, nid: int):
        if self._nid == nid:
            return self
        if visit.get(self._nid):
            return None
        visit.set(self._nid)
        for def_ in self._inputs:
            if def_ is not None:
                rez = def_._find(visit, nid)
                if rez is not None:
                    return rez
        for use in self._outputs:
            rez = use._find(visit, nid)
            if rez is not None:
                return rez
        return None
    

class ConstantNode(Node):
    def __init__(self, type_: Type):
        from ..parser import Parser
        super().__init__(Parser.START)
        self._con = type_

    @override
    def label(self) -> str:
        return f"#{self._con}"

    @override
    def unique_name(self):
        return f"Con_{self._nid}"

    @override
    def _print1(self, s):
        return self._con._print(s)

    @override
    def compute(self):
        return self._con

    @override
    def idealize(self):
        return None

class ReturnNode(Node):
    def __init__(self, ctrl, data):
        super().__init__(ctrl, data)

    def ctrl(self) -> Node:
        return self.In(0)

    def expr(self) -> Node:
        return self.In(1)

    @override
    def label(self) -> str:
        return "Return"

    @override
    def _print1(self, s: str):
        return self.expr()._print0(s + "return ") + ";"

    def isCFG(self) -> bool:
        return True

    @override
    def compute(self):
        return TypeTuple([self.ctrl()._type, self.expr()._type])

    @override
    def idealize(self):
        return None

class MultiNode(Node):
    def __init__(self, *args):
        super().__init__(*args)

class StartNode(MultiNode):
    def __init__(self, variables):
        super().__init__()
        self._args = TypeTuple(variables)
        self._type = self._args

    @override
    def label(self) -> str:
        return "Start"

    @override
    def _print1(self, s: str):
        return s + self.label()

    def isCFG(self) -> bool:
        return True

    @override
    def compute(self):
        return self._args

    @override
    def idealize(self):
        return None

class StopNode(Node):
    def __init__(self, *inputs):
        super().__init__(*inputs)

    @override
    def label(self) -> str:
        return "Stop"
    
    @override
    def _print1(self, s: str):
        if self.ret() is not None: return s + self.ret()._print0(s)
        s += "Stop[ "
        for ret in self._inputs:
            s = ret._print0(s)
            s += " "
        return s + "]"
    
    @override
    def isCFG(self) -> bool:
        return True
    
    def ret(self):
        """
            If a single Return, return it.
            Otherwise, null because ambiguous.
        """
        return self.In(0) if self.nIns() == 1 else None
    
    @override
    def compute(self):
        return BOTTOM
    
    @override
    def idealize(self):
        return None

    def add_return(self, node):
        return self.add_def(node)