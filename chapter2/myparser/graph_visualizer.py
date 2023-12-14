from .node import ConstantNode, StartNode

class GraphVisualizer:
    """Simple visualizer that outputs GraphViz dot format.
       The dot output must be saved to a file and run manually via dot to generate the SVG output.
       Currently, this is done manually.
    """
    def __init__(self) -> None:
        super().__init__()

    def generate_dot_output(self, parser) -> str:
        # graph may have cycles, get all nodes in graph first.
        all_nodes = self.find_all(parser)
        s = f"digraph chapter02\n"
        s += "/*\n"
        s += parser.src()
        s += "\n*/\n"

        s += "\trandir=BT;\n"
        s += "\tordering=\"in\";\n"
        s += "\tconcentrate=\"true\";\n"

        s = self.nodes(s, all_nodes)

        s = self.node_edges(s, all_nodes)

        s += "}\n"
        return s

    def nodes(self, s, all_nodes):
        s += "\tsubgraph cluster_Nodes {\n"
        for node in all_nodes:
            s += f"\t\t{node.unique_name()} [ "
            lab = node.glabel()
            if node.isCFG():
                s += "shape=box style=filled fillcolor=yellow "
            s += f"lable=\"{lab}\""
            s += "];\n"
        s += "\t}\n"
        return s

    # walk through node edges
    def node_edges(self, s, all_nodes):
        s += "\tedge [ fontname=Helvetica fontsize=8 ];\n"
        for node in all_nodes:
            i = 0
            for def_ in node._inputs:
                s += f"\t{node.unique_name()} -> "
                s += f"{def_.unique_name()}"
                # number edges
                s += f"[taillabel={i}]"
                if isinstance(node, ConstantNode) and isinstance(def_, StartNode):
                    s += " style=dotted"
                elif def_.isCFG():
                    s += " color=red"
                s += "];\n"
            i +=1
        return s

    def find_all(self, parser):
        start = parser.start
        all_nodes = []
        for n in start._outputs:
            self.walk(all_nodes, n)
        return all_nodes

    def walk(self, all_nodes, node):
        if node in all_nodes:
            return
        all_nodes.append(node)
        for c in node._inputs:
            self.walk(all_nodes, c)
        for c in node._outputs:
            self.walk(all_nodes, c)
