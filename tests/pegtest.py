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
from typing.re import Pattern
# PEG package
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
from pegparser import PEG
# #### Tests ######################################################### #
class TestGrammars(unittest.TestCase):
    
    def test_basic_grammar(self):
        g = PEG.grammar('base', '[0-9]')
        self.assertEqual(PEG.parse('1234-5678', g), ('234-5678', ('base','1')))
        
    def test_sequence(self):
        g = PEG.grammar('seq', '0', '[1-9]+', '-')
        self.assertEqual(PEG.parse('01234-5678', g), ('5678', ('seq','01234-')))

    def test_ordered(self):
        g = PEG.grammar("ord", "-", PEG.ordered('[0-9]', '[a-z]'))
        self.assertEqual(PEG.parse('-01234', g), ('1234', ('ord','-0')))
        self.assertEqual(PEG.parse('-a1234', g), ('1234', ('ord','-a')))
    
    def test_zeroMore(self):
        g = PEG.grammar("zero", '-', PEG.zeroMore('[a-z]'), '.')
        self.assertEqual(PEG.parse("-abcd1234", g), ('234', ('zero', '-abcd1')))
        self.assertEqual(PEG.parse("-1234abcd", g), ('234abcd', ('zero', '-1')))
    
    def test_oneMore(self):
        g = PEG.grammar("one", '-', PEG.oneMore('[a-z]'), '.')
        self.assertEqual(PEG.parse("-abcd1234", g), ('234', ('one', '-abcd1')))
        self.assertEqual(PEG.parse("-1234abcd", g), ('1234abcd', ('one', '-')))
    
    def test_optional(self):
        g = PEG.grammar("opt", '-', PEG.optional('[a-z]'), '.')
        self.assertEqual(PEG.parse("-abcd1234", g), ('cd1234', ('opt', '-ab')))
        self.assertEqual(PEG.parse("-1234abcd", g), ('234abcd', ('opt', '-1')))
    
    def test_andPred(self):
        g = PEG.grammar("and", '-', PEG.andPred('[0-9]'), '.')
        self.assertEqual(PEG.parse("-01234abcd", g), ('1234abcd', ('and', '-0')))
        self.assertEqual(PEG.parse("-abcd1234", g), ('abcd1234', ('and', '-')))
        
    def test_notPred(self):
        g = PEG.grammar("not", '-', PEG.notPred('[0-9]'), '.')
        self.assertEqual(PEG.parse("-01234abcd", g), ('01234abcd', ('not', '-')))
        self.assertEqual(PEG.parse("-abcd1234", g), ('bcd1234', ('not', '-a')))
    
    def test_tr(self):
        g0 = PEG.tr('[0-9]', '[a-z]', name="tr_seq")
        g1 = PEG.tr('/', '[0-9]', '[a-z]', name="tr_ord")
        g2 = PEG.tr('*', '[0-9]', '[a-z]', name='tr_zero')
        g3 = PEG.tr('+', '[0-9]', '[a-z]', name='tr_one')
        g4 = PEG.tr('?', '[0-9]', '[a-z]', name='tr_opt')
        g5 = PEG.tr('&', '[0-9]', '[a-z]', name='tr_and')
        g6 = PEG.tr('!', '[0-9]', '[a-z]', name='tr_not')
        self.assertEqual(PEG.parse('0a', g0), ('', ('tr_seq', '0a')))
        self.assertEqual(PEG.parse('0a', g1), ('a', ('tr_ord', '0')))
        self.assertEqual(PEG.parse('aa0000aaa', g2), ('0000aaa', ('tr_zero', 'aa')))
        self.assertEqual(PEG.parse('000aaa', g3), ('', ('tr_one', '000aaa')))
        self.assertEqual(PEG.parse('a0a', g4), ('0a', ('tr_opt', 'a')))
        self.assertEqual(PEG.parse('0a', g5), ('0a', []))
        self.assertEqual(PEG.parse('a0a', g5), ('a0a', None))
        self.assertEqual(PEG.parse('0a', g6), ('0a', None))
        self.assertEqual(PEG.parse('a0a', g6), ('a0a', []))

# #### Testing ####################################################### #
if __name__ == '__main__':
    unittest.main()
