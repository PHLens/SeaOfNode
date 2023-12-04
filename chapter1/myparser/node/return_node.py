from .node import Node

class ReturnNode(Node):
    def __init__(self, *args):
        super().__init__(self, *args)

    def ctrl(self) -> Node:
        return self.In(0)

    def expr(self) -> Node:
        return self.In(1)

    def isCFG(self) -> bool:
        return True;
