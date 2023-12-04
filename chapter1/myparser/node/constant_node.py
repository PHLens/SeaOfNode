from .node import Node

class ConstantNode(Node):
    # pass start node to init since python has import issue.
    def __init__(self, value: int, start_node):
        self._value = value
        super().__init__(self, start_node)

    def __repr__(self) -> str:
        return super().__repr__() + f"(value: {self._value})"
