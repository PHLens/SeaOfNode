import unittest
import os
import sys
cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(cur_dir + "/../")
from myparser.parser import Parser
from myparser.node import Node
from common_utils import testinfo

class TestParser(unittest.TestCase):
    #@testinfo()
    def test_parser_grammar(self):
        Node._disablePeephole = True
        parser = Parser("return 1+2*3+-5;")
        ret = parser.parse()
        self.assertEqual("return (1+((2*3)+(-5)));", ret.print())
        gv = GraphVisualizer()
        print(gv.generate_dot_output(parser))
        Node._disablePeephole = False


if __name__ == '__main__':
    unittest.main()
