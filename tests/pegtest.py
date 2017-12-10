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
import pegparser as peg

# #### Tests ######################################################### #
class TestGrammars(unittest.TestCase):
    
    def test_defGrammar(self):
        ast = []
        x = peg.defGrammar('x', '1 ')
        res = x.parse("1 and 2", ast)
        self.assertEqual(res, (True, 'and 2'))
        self.assertEqual(ast, [('x', '1 ')])
    
    def test_sequence(self):
        ast = []
        g_add = peg.defGrammar('a', ' \+ ')
        g = peg.PEG.sequence('add', peg.PEG.NUMBER, g_add, peg.PEG.NUMBER, isConv=True)
        self.assertTrue(peg.PEG.parse('1 + 2', g, ast))
        self.assertEqual(ast, [('add', '1 + 2')])
    
    def test_ordered(self):
        ast1 = []
        ast2 = []
        g = peg.PEG.ordered('num or str', peg.PEG.NUMBER, peg.PEG.STRINGS, isConv=True, isSkip=True)
        self.assertTrue(peg.PEG.parse('1 test', g, ast1))
        self.assertEqual(ast1, [('num or str', '1')])
        self.assertTrue(peg.PEG.parse('test 1', g, ast2))
        self.assertEqual(ast2, [('num or str', 'test')])
    
    def test_zeroOrMore(self):
        ast1 = []
        ast2 = []
        g = peg.PEG.zeroOrMore('oneline', peg.defGrammar('1', '1'), isConv=True, isSkip=True)
        self.assertTrue(peg.PEG.parse('11111111111111112', g, ast1))
        self.assertEqual(ast1, [('oneline', '1111111111111111')])
        self.assertTrue(peg.PEG.parse('1111 1111 1111 1111 2', g, ast2))
        self.assertEqual(ast2, [('oneline', '1111111111111111')])
    
    def test_oneOrMore(self):
        ast1 = []
        ast2 = []
        g = peg.PEG.oneOrMore('some', peg.PEG.STRINGS, isConv=True, isSkip=True)
        self.assertTrue(peg.PEG.parse('qwerty1uiop', g, ast1))
        self.assertEqual(ast1, [('some', 'qwerty')])
        self.assertTrue(peg.PEG.parse('q w e r t y 1 u i o p', g, ast2))
        self.assertEqual(ast2, [('some', 'qwerty')])
    
    def test_optional(self):
        ast1 = []
        ast2 = []
        g = peg.PEG.optional('option', peg.PEG.NUMBER, isConv=True, isSkip=True)
        self.assertTrue(peg.PEG.parse('1', g, ast1))
        self.assertEqual(ast1, [('option', '1')])
        self.assertTrue(peg.PEG.parse(' a', g, ast2))
        self.assertEqual(ast2, [])
    
    def test_andPred(self):
        ast1 = []
        ast2 = []
        g = peg.PEG.andPred('andtest', peg.PEG.NUMBER, isConv=True, isSkip=True)
        self.assertTrue(peg.PEG.parse('1', g, ast1))
        self.assertEqual(ast1, [])
        self.assertFalse(peg.PEG.parse('a', g, ast2))
        self.assertEqual(ast2, [])
        
    def test_notPred(self):
        ast1 = []
        ast2 = []
        g = peg.PEG.notPred('nottest', peg.PEG.NUMBER, isConv=True, isSkip=True)
        self.assertTrue(peg.PEG.parse('a', g, ast1))
        self.assertEqual(ast1, [])
        self.assertFalse(peg.PEG.parse('1', g, ast2))
        self.assertEqual(ast2, [])

# #### Testing ####################################################### #
if __name__ == '__main__':
    unittest.main()
