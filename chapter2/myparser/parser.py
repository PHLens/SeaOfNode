from .node import *

class Parser():
    # class variable for static use.
    start = None
    def __init__(self, source: str):
        self.start = StartNode()
        self._lexer = self.Lexer(source)
        Node.reset()

    def src(self) -> str:
        return str(self._lexer._input)

    def parse(self) -> ReturnNode:
        self.require("return")
        return self.parseReturn()

    def parseReturn(self) -> ReturnNode:
        expr = self.require(";", self.parseExpression())
        return ReturnNode(self.start, expr)

    def parseExpression(self):
        return self.parsePrimary()

    def parsePrimary(self):
        self._lexer.skipWhiteSpace()
        if self._lexer.isNumber():
            return self.parseIntegerLiteral()
        raise self.error("Syntax error, expected integer literal")

    def parseIntegerLiteral(self) -> ConstantNode:
        return ConstantNode(self._lexer.parseNumber(), self.start)

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

        def parseNumber(self):
            start = self._position
            ch = self.nextChar()
            while self.isNumber(ch):
                ch = self.nextChar()
            snum = self._input[start:self._position - 1]
            self._position -= 1
            if len(snum) > 1 and snum[0] == '0':
                raise Parser.error("Syntax error: integer values cannot start with '0'")

            return int(snum)

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
