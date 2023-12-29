from .node import *
from .type import *
from .graph_visualizer import GraphVisualizer

class Parser():
    """
        The Parser converts a Simple source program to the Sea of Nodes intermediate
        representation directly in one pass. There is no intermediate Abstract
        Syntax Tree structure.
        
        This is a simple recursive descent parser. All lexical analysis is done here as well.
    """
    # class variable for static use.
    START = None
    # List of keywords disallowed as identifiers.
    KEYWORDS = ["int", "return"]
    def __init__(self, source: str, arg=None):
        if arg is None:
            arg = BOT
        Node.reset()
        self._lexer = self.Lexer(source)
        self._scope = ScopeNode()
        Parser.START = StartNode([CONTROL, arg])
        Parser.START.peephole()

    def __repr__(self):
        return self._lexer.__repr__()

    def src(self) -> str:
        return str(self._lexer._input)
    
    def find(self, nid):
        """
            Debugging utility to find a Node by index
        """
        return Parser.START.find(nid)

    def ctrl(self):
        return self._scope.ctrl()
    
    def ctrln(self, n):
        return self._scope.ctrln(n)

    def parse(self, show=False) -> ReturnNode:
        # Enter a new scope for the initial control and arguments
        self._scope.push()
        self._scope.define(ScopeNode.CTRL, ProjNode(Parser.START, 0, ScopeNode.CTRL).peephole())
        self._scope.define(ScopeNode.ARG0, ProjNode(Parser.START, 1, ScopeNode.ARG0).peephole())
        ret = self.parseBlock()
        self._scope.pop()
        if not self._lexer.is_eof():
            self.error(f"Syntax error, unexpected {self._lexer.getAnyNextToken()}")
        if show:
            self.showGraph()
        return ret

    def parseBlock(self):
        """ Block
            '{' statement '}'
            Does not parse the opening or closing '{}'
        """
        # Enter a new scope
        self._scope.push()
        n = None
        while not self.peek('}') and not self._lexer.is_eof():
            n0 = self.parseStatement()
            if n0 is not None:
                n = n0
        # Exit scope
        self._scope.pop()
        return n

    def parseStatement(self):
        """ Parses a statement:
            returnStatement | declStatement | blockStatement | expressionStatement
        """
        if self.matchx("return"): return self.parseReturn()
        elif self.matchx("int"): return self.parseDecl()
        elif self.match("{"): return self.require(self.parseBlock(), "}")
        elif self.matchx("#showGraph"): return self.require(self.showGraph(), ";")
        else: return self.parseExpressionStatement()

    def parseReturn(self) -> ReturnNode:
        """ Parses a return statement; "return" already parsed.
            The $ctrl edge is killed

            'return' expr ;
        """
        expr = self.require(self.parseExpression(), ";")
        ret = ReturnNode(self.ctrl(), expr).peephole()
        self.ctrln(None)  # kill control
        return ret

    def showGraph(self):
        """
            Dumps out the node graph
        """
        with open("graph.dot", 'w') as f:
            f.write(GraphVisualizer().generate_dot_output(self))
        import os
        os.system("dot -Tpng graph.dot -o graph.png")
        return None

    def parseExpressionStatement(self):
        """ Parses an expression statement
            name '=' expression ';'
        """
        name = self.requireId()
        self.require(syntax="=")
        expr = self.require(self.parseExpression(), ";")
        if self._scope.update(name, expr) == None:
            self.error(f"Undefined name '{name}'")
        return expr

    def parseDecl(self):
        """ Parses a declStatement
            'int' name = expression ';'
        """
        # Type is `int` for now.
        name = self.requireId()
        self.require(syntax="=")
        expr = self.require(self.parseExpression(), ";")
        if self._scope.define(name, expr) == None:
            self.error(f"Redefining name '{name}'")
        return expr

    def parseExpression(self):
        """ Parse an expression of the form:
            expr : compareExpr
        """
        return self.parseComparison()

    def parseComparison(self):
        """ Parse an expression of the form:
            compareExpr : additiveExpr op additiveExpr
        """
        lhs = self.parseAddition()
        if self.match("=="): return EQ(lhs, self.parseComparison()).peephole()
        if self.match("!="): return NotNode(EQ(lhs, self.parseComparison()).peephole()).peephole()
        if self.match("<"): return LT(lhs, self.parseComparison()).peephole()
        if self.match("<="): return LE(lhs, self.parseComparison()).peephole()
        if self.match(">"): return LE(self.parseComparison(), lhs).peephole()
        if self.match(">="): return LE(self.parseComparison(), lhs).peephole()
        return lhs

    def parseAddition(self):
        """ Parse an additive expression
            additiveExpr : multiplicativeExpr (('+' | '-') multiplicativeExpr)*
        """
        lhs = self.parseMultiplication()
        if self.match("+"): return AddNode(lhs, self.parseAddition()).peephole()
        if self.match("-"): return SubNode(lhs, self.parseAddition()).peephole()
        return lhs

    def parseMultiplication(self):
        """
            multiplicativeExpr : unaryExpr (('*' | '/') unaryExpr)*
        """
        lhs = self.parseUnary()
        if self.match("*"): return MulNode(lhs, self.parseMultiplication()).peephole()
        if self.match("/"): return DivNode(lhs, self.parseMultiplication()).peephole()
        return lhs

    def parseUnary(self):
        """
            unaryExpr : ('-') unaryExpr | primaryExpr
        """
        if self.match("-"): return MinusNode(self.parseUnary()).peephole()
        return self.parsePrimary()

    def parsePrimary(self):
        """
            primaryExpr : integerLiteral | Identifier | '(' expression ')'
        """
        if self._lexer.isNumber():
            return self.parseIntegerLiteral()
        if self.match("("): return self.require(self.parseExpression(), ")")
        name = self._lexer.matchId()
        if name == None: self.errorSyntax("an identifier or expression")
        n = self._scope.lookup(name)
        if n is not None: return n
        self.error(f"Undefined name '{name}'")

    def parseIntegerLiteral(self) -> ConstantNode:
        """
            integerLiteral: [1-9][0-9]* | [0]
        """
        return ConstantNode(self._lexer.parseNumber()).peephole()

    #----------------------------------#
    # Utilities for lexical analysis

    def match(self, syntax: str):
        """
            return True and skip if "syntax" is next in the steam.
        """
        return self._lexer.match(syntax)
    
    def matchx(self, syntax: str):
        """
            Match must be "exact", not be followed by more id letters.
        """
        return self._lexer.matchx(syntax)
    
    def peek(self, ch: str):
        """
            Return True and do NOT skip if 'ch' is next
        """
        return self._lexer.peekeq(ch)

    def requireId(self):
        """
            Require and return an identifier.
        """
        id_ = self._lexer.matchId()
        if id_ is not None and not id_ in Parser.KEYWORDS:
            return id_
        self.error(f"Expected an identifier, but found '{id_}'")

    # require exact match
    def require(self, n=None, syntax="") -> Node:
        if self.match(syntax):
            return n
        self.errorSyntax(syntax)

    def errorSyntax(self, syntax):
        return self.error(f"Syntax error, expected {syntax}: {self._lexer.getAnyNextToken()}")
    
    @staticmethod
    def error(errorMessage):
        raise RuntimeError(errorMessage)

    #---------------------------------#
    # Lexer Components

    class Lexer():
        def __init__(self, source):
            self._input = source
            self._position = 0

        def __repr__(self) -> str:
            return self._input[self._position:len(self._input) - self._position]

        def is_eof(self):
            return self._position >= len(self._input)

        # use '#' for EOF
        def peek(self):
            import sys
            return chr(sys.maxunicode) if self.is_eof() else str(self._input[self._position])

        def nextChar(self):
            ch = self.peek()
            self._position = self._position + 1
            return ch

        def isWhiteSpace(self):
            return self.peek() <= ' '

        def skipWhiteSpace(self):
            while self.isWhiteSpace():
                self._position = self._position + 1
        
        # Return true, if we find "syntax" after skipping white space; also
        # then advance the cursor past syntax.
        # Return false otherwise, and do not advance the cursor.
        def match(self, syntax):
            self.skipWhiteSpace()
            lenth = len(syntax)
            if self._position + lenth > len(self._input):
                return False
            for i in range(lenth):
                if self._input[self._position + i] != syntax[i]:
                    return False
            self._position = self._position + lenth
            return True
        
        def matchx(self, syntax):
            if not self.match(syntax):
                return False
            if not self.isIdLetter(self.peek()):
                return True
            self._position = self._position - len(syntax)
            return False

        def peekeq(self, ch:str):
            self.skipWhiteSpace()
            return self.peek() == ch

        def matchId(self):
            """
                Return an identifier or None.
            """
            self.skipWhiteSpace()
            return self.parseId() if self.isIdStart(self.peek()) else None

        def getAnyNextToken(self):
            if self.is_eof():
                return ""
            if self.isIdStart(self.peek()):
                return self.parseId()
            if self.isPunctuation(self.peek()):
                return self.parsePunctuation()
            return str(self.peek())

        def isNumber(self, ch=None):
            if ch is None:
                ch = self.peek()
            return ch.isdigit()

        def parseNumber(self) -> Type:
            start = self._position
            ch = self.nextChar()
            while self.isNumber(ch):
                ch = self.nextChar()
            snum = self._input[start:self._position - 1]
            self._position -= 1
            if len(snum) > 1 and snum[0] == '0':
                raise Parser.error("Syntax error: integer values cannot start with '0'")

            return TypeInteger.constant(int(snum))

        def isIdStart(self, ch: str):
            return ch.isalpha() or ch == '_'

        def isIdLetter(self, ch: str):
            return ch.isalpha() or ch.isdigit() or ch == '_'

        def parseId(self):
            start = self._position
            ch = self.nextChar()
            while self.isIdLetter(ch):
                ch = self.nextChar()
            parsed_id = self._input[start:self._position - 1]
            self._position -= 1
            return parsed_id

        def isPunctuation(self, ch: str):
            return "=;[]<>()+-/*".find(ch) != -1

        def parsePunctuation(self):
            start = self._position
            return self._input[start:start + 1]
