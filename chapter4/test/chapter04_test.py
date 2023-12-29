import unittest
import os
import sys
cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(cur_dir + "/../")
from myparser.parser import Parser
from myparser.graph_visualizer import GraphVisualizer
from myparser.node import Node, ConstantNode, ProjNode
from myparser.type import TypeInteger, BOT

class TestParser(unittest.TestCase):
    def test_chapter4_peephole(self):
        parser = Parser("return 1+arg+2; #showGraph;")
        ret = parser.parse()
        self.assertEqual("return (arg+3);", ret.print())

    def test_chapter4_peephole2(self):
        parser = Parser("return (1+arg)+2;")
        ret = parser.parse()
        self.assertEqual("return (arg+3);", ret.print())
    
    def test_chapter4_add0(self):
        parser = Parser("return 0+arg;")
        ret = parser.parse()
        self.assertEqual("return arg;", ret.print())
    
    def test_chapter4_add_add_mul(self):
        parser = Parser("return arg+0+arg;")
        ret = parser.parse()
        self.assertEqual("return (arg*2);", ret.print())
    
    def test_chapter4_peephole3(self):
        parser = Parser("return 1+arg+2+arg+3;")
        ret = parser.parse()
        self.assertEqual("return ((arg*2)+6);", ret.print())
    
    def test_chapter4_mul1(self):
        parser = Parser("return 1*arg;")
        ret = parser.parse()
        self.assertEqual("return arg;", ret.print())
    
    def test_chapter4_var_arg(self):
        parser = Parser("return arg; #showGraph;", BOT)
        ret = parser.parse()
        self.assertTrue(isinstance(ret.In(0), ProjNode))
        self.assertTrue(isinstance(ret.In(1), ProjNode))

    def test_chapter4_constant_arg(self):
        parser = Parser("return arg;", TypeInteger.constant(2))
        ret = parser.parse()
        self.assertEqual("return 2;", ret.print())

    def test_chapter4_comp_eq(self):
        parser = Parser("return 3==3; #showGraph;")
        ret = parser.parse()
        self.assertEqual("return 1;", ret.print())

    def test_chapter4_comp_eq2(self):
        parser = Parser("return 3==4; #showGraph;")
        ret = parser.parse()
        self.assertEqual("return 0;", ret.print())
    
    def test_chapter4_comp_neq(self):
        parser = Parser("return 3!=3; #showGraph;")
        ret = parser.parse()
        self.assertEqual("return 0;", ret.print())

    def test_chapter4_comp_neq2(self):
        parser = Parser("return 3!=4; #showGraph;")
        ret = parser.parse()
        self.assertEqual("return 1;", ret.print())
    
    def test_chapter4_comp_bug1(self):
        parser = Parser("int a=arg+1; int b=a; b=1; return a+2; #showGraph;")
        ret = parser.parse()
        self.assertEqual("return (arg+3);", ret.print())
    
    def test_chapter4_comp_bug2(self):
        parser = Parser("int a=arg+1; a=a; return a; #showGraph;")
        ret = parser.parse()
        self.assertEqual("return (arg+1);", ret.print())
    
    def test_chapter4_comp_bug3(self):
        parser = Parser("inta=1; return a;")
        msg = "Undefined name 'inta'"
        with self.assertRaisesRegex(RuntimeError, msg):
            ret = parser.parse()
    
    def test_chapter4_comp_bug4(self):
        parser = Parser("return -arg;")
        ret = parser.parse()
        self.assertEqual("return (-arg);", ret.print())

    def test_var_decl(self):
        parser = Parser("int a=1; return a;")
        ret = parser.parse()
        self.assertEqual("return 1;", ret.print())

    def test_var_add(self):
        parser = Parser("int a=1; int b=2; return a+b;")
        ret = parser.parse()
        self.assertEqual("return 3;", ret.print())

    def test_var_scope(self):
        parser = Parser("int a=1; int b=2; int c=0; { int b=3; c=a+b; } return c;")
        ret = parser.parse()
        self.assertEqual("return 4;", ret.print())

    def test_var_scope_nopeephole(self):
        parser = Parser("int a=1; int b=2; int c=0; { int b=3; c=a+b; #showGraph; } return c; #showGraph;")
        Node._disablePeephole = True
        ret = parser.parse()
        Node._disablePeephole = False
        self.assertEqual("return (1+3);", ret.print())

    def test_var_dist(self):
        parser = Parser("int x0=1; int y0=2; int x1=3; int y1=4; return (x0-x1)*(x0-x1) + (y0-y1)*(y0-y1); #showGraph;")
        ret = parser.parse()
        self.assertEqual("return 8;", ret.print())

    def test_self_assign(self):
        parser = Parser("int a=a; return a;")
        refmsg = "Undefined name 'a'"
        with self.assertRaisesRegex(RuntimeError, refmsg):
            ret = parser.parse()

    def test_chapter2_parser_grammar(self):
        parser = Parser("return 1+2*3+-5;")
        Node._disablePeephole = True
        ret = parser.parse()
        self.assertEqual("return (1+((2*3)+(-5)));", ret.print())
        gv = GraphVisualizer()
        print(gv.generate_dot_output(parser))
        Node._disablePeephole = False

    def test_chapter2_add_peephole(self):
        parser = Parser("return 1+2;")
        ret = parser.parse()
        self.assertEqual("return 3;", ret.print())

    def test_chapter2_sub_peephole(self):
        parser = Parser("return 1-2;")
        ret = parser.parse()
        self.assertEqual("return -1;", ret.print())

    def test_chapter2_mul_peephole(self):
        parser = Parser("return 2*3;")
        ret = parser.parse()
        self.assertEqual("return 6;", ret.print())

    def test_chapter2_div_peephole(self):
        parser = Parser("return 6/3;")
        ret = parser.parse()
        self.assertEqual("return 2;", ret.print())

    def test_chapter2_minus_peephole(self):
        parser = Parser("return 6/-3;")
        ret = parser.parse()
        self.assertEqual("return -2;", ret.print())

    def test_chapter2_example(self):
        parser = Parser("return 1+2*3+-5;")
        ret = parser.parse()
        self.assertEqual("return 2;", ret.print())

    def test_simple_program(self):
        parser = Parser("return 1;")
        ret = parser.parse()
        start = parser.START

        self.assertTrue(isinstance(ret.ctrl(), ProjNode))
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
        reg_msg = f"Syntax error, expected =:"
        with self.assertRaisesRegex(RuntimeError, reg_msg):
            parser.parse()

    def test_bad2(self):
        parser = Parser("return 0123;")
        reg_msg = f"Syntax error: integer values cannot start with '0'"
        with self.assertRaisesRegex(RuntimeError, reg_msg):
            parser.parse()

    def test_not_bad3(self):
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

    def test_bad6(self):
        parser = Parser("int a=1; int b=2; int c=0; { int b=3; c=a+b;")
        reg_msg = "Syntax error, expected }: "
        with self.assertRaisesRegex(RuntimeError, reg_msg):
            parser.parse()

    def test_bad7(self):
        parser = Parser("return 1;}")
        reg_msg = "Syntax error, unexpected }"
        with self.assertRaisesRegex(RuntimeError, reg_msg):
            parser.parse()

if __name__ == '__main__':
    unittest.main()
