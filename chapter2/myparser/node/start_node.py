from .node import Node

class StartNode(Node):
    def __init__(self):
        super().__init__(self)

    def isCFG(self) -> bool:
        return True;
