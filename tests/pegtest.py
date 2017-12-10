#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2017 N.T.WORKS Authors. All Rights Reserved.
#
#      http://opensource.org/licenses/mit-license.php
#

""" Test package.
"""

# #### Imports ####################################################### #
# Builtin
import os
import sys
import unittest
import re
# PEG package
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
from pegparser import PEG

# #### Tests ######################################################### #
class TestGrammars(unittest.TestCase):
    
    def test_defGrammar(self):
        ast = []
        x = PEG.grammar('x', '1 ')
        res = x.parse("1 and 2", ast)
        self.assertEqual(res, (True, 'and 2'))
        self.assertEqual(ast, [('x', '1 ')])
    
    def test_sequence(self):
        ast = []
        g_add = PEG.grammar('a', ' \+ ')
        g = PEG.sequence('add', PEG.NUMBER, g_add, PEG.NUMBER, isConv=True)
        self.assertTrue(PEG.parse('1 + 2', g, ast))
        self.assertEqual(ast, [('add', '1 + 2')])
    
    def test_ordered(self):
        ast1 = []
        ast2 = []
        g = PEG.ordered('num or str', PEG.NUMBER, PEG.STRINGS, isConv=True, isSkip=True)
        self.assertTrue(PEG.parse('1 test', g, ast1))
        self.assertEqual(ast1, [('num or str', '1')])
        self.assertTrue(PEG.parse('test 1', g, ast2))
        self.assertEqual(ast2, [('num or str', 'test')])
    
    def test_zeroOrMore(self):
        ast1 = []
        ast2 = []
        g = PEG.zeroOrMore('oneline', PEG.grammar('1', '1'), isConv=True, isSkip=True)
        self.assertTrue(PEG.parse('11111111111111112', g, ast1))
        self.assertEqual(ast1, [('oneline', '1111111111111111')])
        self.assertTrue(PEG.parse('1111 1111 1111 1111 2', g, ast2))
        self.assertEqual(ast2, [('oneline', '1111111111111111')])
    
    def test_oneOrMore(self):
        ast1 = []
        ast2 = []
        g = PEG.oneOrMore('some', PEG.STRINGS, isConv=True, isSkip=True)
        self.assertTrue(PEG.parse('qwerty1uiop', g, ast1))
        self.assertEqual(ast1, [('some', 'qwerty')])
        self.assertTrue(PEG.parse('q w e r t y 1 u i o p', g, ast2))
        self.assertEqual(ast2, [('some', 'qwerty')])
    
    def test_optional(self):
        ast1 = []
        ast2 = []
        g = PEG.optional('option', PEG.NUMBER, isConv=True, isSkip=True)
        self.assertTrue(PEG.parse('1', g, ast1))
        self.assertEqual(ast1, [('option', '1')])
        self.assertTrue(PEG.parse(' a', g, ast2))
        self.assertEqual(ast2, [])
    
    def test_andPred(self):
        ast1 = []
        ast2 = []
        g = PEG.andPred('andtest', PEG.NUMBER, isConv=True, isSkip=True)
        self.assertTrue(PEG.parse('1', g, ast1))
        self.assertEqual(ast1, [])
        self.assertFalse(PEG.parse('a', g, ast2))
        self.assertEqual(ast2, [])
        
    def test_notPred(self):
        ast1 = []
        ast2 = []
        g = PEG.notPred('nottest', PEG.NUMBER, isConv=True, isSkip=True)
        self.assertTrue(PEG.parse('a', g, ast1))
        self.assertEqual(ast1, [])
        self.assertFalse(PEG.parse('1', g, ast2))
        self.assertEqual(ast2, [])

# #### Testing ####################################################### #
if __name__ == '__main__':
    unittest.main()
