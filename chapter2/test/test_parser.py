import unittest
import os
import sys
cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(cur_dir + "/../")
from myparser import Parser, ConstantNode
from common_utils import testinfo

class TestParser(unittest.TestCase):
    #@testinfo()
    def test_simple_program(self):
        parser = Parser("return 1;")
        ret = parser.parse()
        start = parser.start

        self.assertIs(start, ret.ctrl())
        expr = ret.expr()
        if isinstance(expr, ConstantNode):
            self.assertIs(start, expr.In(0))
            self.assertEqual(1, expr._value)
        else:
            self.assertTrue(False)

    #@testinfo()
    def test_zero(self):
        parser = Parser("return 0;")
        ret = parser.parse()
        start = parser.start
        for use in start._outputs:
            if isinstance(use, ConstantNode):
                self.assertEqual(0, use._value)

    #@unittest.skip("not test")
    #@testinfo()
    def test_bad1(self):
        parser = Parser("ret")
        reg_msg = f"Syntax error, expected return: ret"
        with self.assertRaisesRegex(RuntimeError, reg_msg):
            parser.parse()

    #@unittest.skip("not test")
    #@testinfo()
    def test_bad2(self):
        parser = Parser("return 0123;")
        reg_msg = f"Syntax error: integer values cannot start with '0'"
        with self.assertRaisesRegex(RuntimeError, reg_msg):
            parser.parse()

    #@unittest.skip("not test")
    #@testinfo()
    def test_bad3(self):
        parser = Parser("return --12;")
        reg_msg = f"Syntax error, expected integer literal"
        with self.assertRaisesRegex(RuntimeError, reg_msg):
            parser.parse()

    #@unittest.skip("not test")
    #@testinfo()
    def test_bad4(self):
        parser = Parser("return 100")
        reg_msg = f"Syntax error, expected ;: "
        with self.assertRaisesRegex(RuntimeError, reg_msg):
            parser.parse()

    #@unittest.skip("not test")
    #@testinfo()
    # negative numbers require unary operators support.
    def test_bad5(self):
        parser = Parser("return -100;")
        reg_msg = f"Syntax error, expected integer literal"
        with self.assertRaisesRegex(RuntimeError, reg_msg):
            parser.parse()

if __name__ == '__main__':
    unittest.main()
