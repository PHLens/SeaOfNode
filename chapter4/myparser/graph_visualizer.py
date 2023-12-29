from .node import ConstantNode, StartNode, ScopeNode, ProjNode, MultiNode
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
        s = "digraph chapter04 {\n"
        s += "/*\n"
        s += parser.src()
        s += "\n*/\n"

        s += "\trankdir=BT;\n"

        # Preserve node input order
        s += "\tordering=\"in\";\n"
        
        # Merge multiple edges hitting the same node.  Makes common shared
        # nodes much prettier to look at.
        s += "\tconcentrate=\"true\";\n"

        # nodes in a cluster, no edges.
        s = self.nodes(s, all)

        # scopes in another cluster, no edges.
        s = self.scopes(s, parser._scope)

        # Walk node edges.
        s = self.node_edges(s, all)

        # Walk scope edges
        s = self.scope_edges(s, parser._scope)

        s += "}\n"
        return s

    def nodes(self, s, all):
        s += "\tsubgraph cluster_Nodes {\n"
        for node in all:
            if isinstance(node, ProjNode) or isinstance(node, ScopeNode):
                continue  # Do not emit, rolled into MultiNode or Scope cluster already
            s += f"\t\t{node.unique_name()} [ "
            lab = node.glabel()
            if isinstance(node, MultiNode):
                # Make a box with the MultiNode on top, and all the projections on the bottom
                s += "shape=plaintext label=<\n"
                s += "\t\t\t<TABLE BORDER=\"0\" CELLBORDER=\"1\" CELLSPACING=\"0\" CELLPADDING=\"4\">\n"
                s += f"\t\t\t<TR><TD BGCOLOR=\"yellow\">{lab}</TD></TR>\n"
                s += "\t\t\t<TR>"
                doProjTable = False
                for use in node._outputs:
                    if isinstance(use, ProjNode):
                        if not doProjTable:
                            doProjTable = True
                            s += "<TD>\n"
                            s += "\t\t\t\t<TABLE BORDER=\"0\" CELLBORDER=\"1\" CELLSPACING=\"0\">\n"
                            s += "\t\t\t\t<TR>"
                        s += f"<TD PORT=\"p{use._idx}\""
                        if use.isCFG(): s+= " BGCOLOR=\"yellow\""
                        s += f">{use.glabel()}</TD>"
                if doProjTable:
                    s += "</TR>\n"
                    s += "\t\t\t\t</TABLE>\n"
                    s += "\t\t\t</TD>"
                s += "</TR>\n"
                s += "\t\t\t</TABLE>>\n\t\t"
            else:
                if node.isCFG():
                    s += "shape=box style=filled fillcolor=yellow "
                s += f"label=\"{lab}\""
            s += "];\n"
        s += "\t}\n"
        return s

    def scopes(self, s, scopenode):
        s += f"\tnode [shape=plaintext];\n"
        level = 0
        for scope in scopenode._scopes:
            scope_name = self.makeScopeName(scopenode, level)
            s += f"\tsubgraph cluster_{scope_name}" + " {\n"
            s += f"\t\t{scope_name}" + " [label=<\n"
            s += "\t\t\t<TABLE BORDER=\"0\" CELLBORDER=\"1\" CELLSPACING=\"0\">\n"
            # add scope level
            s += f"\t\t\t<TR><TD BGCOLOR=\"cyan\">{level}</TD>"
            for name in scope.keys():
                s += f"<TD PORT=\"{self.makePortName(scope_name, name)}\">{name}</TD>"
            s += "</TR>\n"
            s += "\t\t\t</TABLE>>];\n"
            level += 1
        # close all scope clusters.
        s += "\t}" * level
        return s

    def makeScopeName(self, sn: ScopeNode, level: int):
        return sn.unique_name() + f"_{level}"
    
    def makePortName(self, scope_name: str, varName: str):
        return scope_name + "_" + varName

    # walk through node edges
    def node_edges(self, s, all):
        s += "\tedge [ fontname=Helvetica, fontsize=8 ];\n"
        for node in all:
            # Do not display the Constant->Start edge;
            # ProjNodes handled by Multi;
            # ScopeNodes are done separately
            if isinstance(node, ConstantNode) or isinstance(node, ProjNode) or isinstance(node, ScopeNode):
                continue
            i = 0
            for def_ in node._inputs:
                if def_ is not None:
                    s += f"\t{node.unique_name()} -> "
                    if isinstance(def_, ProjNode):
                        mname = def_.ctrl().unique_name()
                        s += f"{mname}:p{def_._idx}"
                    else:
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

    def scope_edges(self, s, scopenode):
        s += f"\tedge [style=dashed color=cornflowerblue];\n"
        level = 0
        for scope in scopenode._scopes:
            scopename = self.makeScopeName(scopenode, level)
            for name in scope.keys():
                def_ = scopenode.In(scope.get(name))
                if def_ == None:
                    continue
                s += f"\t{scopename}:\"{self.makePortName(scopename, name)}\" -> "
                if isinstance(def_, ProjNode):
                    mname = def_.ctrl().unique_name()
                    s += f"{mname}:p{def_._idx}"
                else:
                    s += f"{def_.unique_name()}"
                s += ";\n"
            level += 1
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
