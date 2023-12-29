from .node import ConstantNode, StartNode
class GraphVisualizer:
    """Simple visualizer that outputs GraphViz dot format.
       The dot output must be saved to a file and run manually via dot to generate the SVG output.
       Currently, this is done manually.
    """
    all_nodes = {}
    def __init__(self) -> None:
        super().__init__()
        GraphVisualizer.all_nodes.clear()

    def generate_dot_output(self, parser) -> str:
        # graph may have cycles, get all nodes in graph first.
        all = self.find_all(parser)
        s = "digraph chapter02 {\n"
        s += "/*\n"
        s += parser.src()
        s += "\n*/\n"

        s += "\trankdir=BT;\n"
        s += "\tordering=\"in\";\n"
        s += "\tconcentrate=\"true\";\n"

        s = self.nodes(s, all)

        s = self.node_edges(s, all)

        s += "}\n"
        return s

    def nodes(self, s, all):
        s += "\tsubgraph cluster_Nodes {\n"
        for node in all:
            s += f"\t\t{node.unique_name()} [ "
            lab = node.glabel()
            if node.isCFG():
                s += "shape=box style=filled fillcolor=yellow "
            s += f"label=\"{lab}\""
            s += "];\n"
        s += "\t}\n"
        return s

    # walk through node edges
    def node_edges(self, s, all):
        s += "\tedge [ fontname=Helvetica, fontsize=8 ];\n"
        for node in all:
            i = 0
            for def_ in node._inputs:
                if def_ is not None:
                    s += f"\t{node.unique_name()} -> "
                    s += f"{def_.unique_name()}"
                    # number edges
                    s += f"[taillabel={i}"
                    if isinstance(node, ConstantNode) and isinstance(def_, StartNode):
                        s += " style=dotted"
                    elif def_.isCFG():
                        s += " color=red"
                    s += "];\n"
                i +=1
        return s

    def find_all(self, parser):
        start = parser.START
        all_nodes = {}
        for n in start._outputs:
            self.walk(n, all_nodes)
        return all_nodes.values()

    def walk(self, node, all_nodes):
        if all_nodes.get(node._nid) is not None:
            return
        all_nodes[node._nid] = node
        for c in node._inputs:
            if c != None:
                self.walk(c, all_nodes)
        for c in node._outputs:
            if c != None:
                self.walk(c, all_nodes)
