from .node import *
from .type import *

class Parser():
    # class variable for static use.
    START = None
    def __init__(self, source: str):
        self._lexer = self.Lexer(source)
        Node.reset()
        Parser.START = StartNode()

    def src(self) -> str:
        return str(self._lexer._input)

    def parse(self) -> ReturnNode:
        self.require("return")
        return self.parseReturn()

    """
        'return' expr ;
    """
    def parseReturn(self) -> ReturnNode:
        expr = self.require(";", self.parseExpression())
        return ReturnNode(Parser.START, expr).peephole()

    """
        expr : additiveExpr
    """
    def parseExpression(self):
        return self.parseAddition()

    """
        additiveExpr : multiplicativeExpr (('+' | '-') multiplicativeExpr)*
    """
    def parseAddition(self):
        lhs = self.parseMultiplication()
        if self.match("+"): return AddNode(lhs, self.parseAddition()).peephole()
        if self.match("-"): return SubNode(lhs, self.parseAddition()).peephole()
        return lhs

    """
        multiplicativeExpr : unaryExpr (('*' | '/') unaryExpr)*
    """
    def parseMultiplication(self):
        lhs = self.parseUnary()
        if self.match("*"): return MulNode(lhs, self.parseMultiplication()).peephole()
        if self.match("/"): return DivNode(lhs, self.parseMultiplication()).peephole()
        return lhs

    """
        unaryExpr : ('-') unaryExpr | primaryExpr
    """
    def parseUnary(self):
        if self.match("-"): return MinusNode(self.parseUnary()).peephole()
        return self.parsePrimary()

    """
        primaryExpr : integerLiteral | Identifier | '(' expression ')'
    """
    def parsePrimary(self):
        #self._lexer.skipWhiteSpace()
        if self._lexer.isNumber():
            return self.parseIntegerLiteral()
        if self.match("("): return self.require(")", self.parseExpression())
        raise self.errorSyntax("integer literal")

    """
        integerLiteral: [1-9][0-9]* | [0]
    """
    def parseIntegerLiteral(self) -> ConstantNode:
        return ConstantNode(self._lexer.parseNumber()).peephole()

    def match(self, syntax: str):
        return self._lexer.match(syntax)

    @staticmethod
    def error(errorMessage):
        return RuntimeError(errorMessage)

    def errorSyntax(self, syntax):
        return self.error(f"Syntax error, expected {syntax}: {self._lexer.getAnyNextToken()}")

    def require(self, syntax, n=None) -> Node:
        if self.match(syntax):
            return n
        raise self.errorSyntax(syntax)

    class Lexer():
        def __init__(self, source):
            self._input = source
            self._position = 0

        def is_eof(self):
            return self._position >= len(self._input)

        # use '#' for EOF
        def peek(self):
            return "#" if self.is_eof() else str(self._input[self._position])

        def nextChar(self):
            ch = self.peek()
            self._position = self._position + 1
            return ch

        def isWhiteSpace(self):
            return self.peek() <= ' '

        def skipWhiteSpace(self):
            while self.isWhiteSpace():
                self._position = self._position + 1

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
                return self.isNumber(ch=self.peek())
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
            parsed_id = self._input[start:self._position]
            self._position -= 1
            return parsed_id

        def isPunctuation(self, ch: str):
            return "=;[]<>()+-/*".find(ch) != -1

        def parsePunctuation(self):
            start = self._position
            return self._input[start:start + 1]

        def __repr__(self) -> str:
            return self._input[self._position:len(self._input) - self._position]
