import unittest
import os
import sys
cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(cur_dir + "/../")
from myparser.parser import Parser
from myparser.graph_visualizer import GraphVisualizer
from myparser.node import Node, ConstantNode
from myparser.type import TypeInteger

class TestParser(unittest.TestCase):
    def test_parser_grammar(self):
        Node._disablePeephole = True
        parser = Parser("return 1+2*3+-5;")
        ret = parser.parse()
        self.assertEqual("return (1+((2*3)+(-5)));", ret.print())
        gv = GraphVisualizer()
        print(gv.generate_dot_output(parser))
        Node._disablePeephole = False

    def test_add_peephole(self):
        parser = Parser("return 1+2;")
        ret = parser.parse()
        self.assertEqual("return 3;", ret.print())

    def test_sub_peephole(self):
        parser = Parser("return 1-2;")
        ret = parser.parse()
        self.assertEqual("return -1;", ret.print())

    def test_mul_peephole(self):
        parser = Parser("return 2*3;")
        ret = parser.parse()
        self.assertEqual("return 6;", ret.print())

    def test_div_peephole(self):
        parser = Parser("return 6/3;")
        ret = parser.parse()
        self.assertEqual("return 2;", ret.print())

    def test_minus_peephole(self):
        parser = Parser("return 6/-3;")
        ret = parser.parse()
        self.assertEqual("return -2;", ret.print())

    def test_example(self):
        parser = Parser("return 1+2*3+-5;")
        ret = parser.parse()
        self.assertEqual("return 2;", ret.print())

    def test_simple_program(self):
        parser = Parser("return 1;")
        ret = parser.parse()
        start = parser.START

        self.assertIs(start, ret.ctrl())
        expr = ret.expr()
        if isinstance(expr, ConstantNode):
            self.assertIs(start, expr.In(0))
            self.assertEqual(TypeInteger.constant(1), expr._type)
        else:
            self.assertTrue(False)

    def test_zero(self):
        parser = Parser("return 0;")
        ret = parser.parse()
        start = parser.START
        for use in start._outputs:
            if isinstance(use, ConstantNode):
                self.assertEqual(TypeInteger.constant(0), use._type)

    def test_bad1(self):
        parser = Parser("ret")
        reg_msg = f"Syntax error, expected return: ret"
        with self.assertRaisesRegex(RuntimeError, reg_msg):
            parser.parse()

    def test_bad2(self):
        parser = Parser("return 0123;")
        reg_msg = f"Syntax error: integer values cannot start with '0'"
        with self.assertRaisesRegex(RuntimeError, reg_msg):
            parser.parse()

    def test_bad3(self):
        parser = Parser("return --12;")
        ret = parser.parse()
        # used to fail in chapter 1
        self.assertEqual("return 12;", ret.print())

    def test_bad4(self):
        parser = Parser("return 100")
        reg_msg = f"Syntax error, expected ;: "
        with self.assertRaisesRegex(RuntimeError, reg_msg):
            parser.parse()

    def test_bad5(self):
        parser = Parser("return -100;")
        ret = parser.parse()
        # used to fail in chapter 1
        self.assertEqual("return -100;", ret.print())

if __name__ == '__main__':
    unittest.main()
