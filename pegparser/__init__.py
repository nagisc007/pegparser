#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2017 N.T.WORKS Authors. All Rights Reserved.
#
#      http://opensource.org/licenses/mit-license.php
#

# #### Imports ####################################################### #
from functools import wraps
from inspect import isfunction
from typing import Callable
# #### Defines ####################################################### #

# #### Functions ##################################################### #
def _skipSpace(src: str) -> str: return src.lstrip()

def _reduceListVals(src) -> str:
    def _toStr(s):
        if isinstance(s, str): return s
        if isinstance(s, (list, tuple)):
            if len(s) == 2: return s[1]
            return "".join([_toStr(x) for x in s])
        else:
            return ""
    return _toStr(src)

def defGrammar(name: str, pattern: str, isSkip=False) -> Callable:
    @wraps(defGrammar)
    def _parser(src: str, ast: list, isSkip=isSkip):
        _m = re.match(pattern, _skipSpace(src) if isSkip else src)
        if _m:
            if not ast is None:
                ast.append((name, _m.group(0)))
            return True, src[len(str(_m.group(0))):]
        return False, src
    return _parser

# #################################################################### #
#   PEG class
# #################################################################### #
class PEG(object):
    BR          = defGrammar('breakline', '\n')
    SPACE       = defGrammar('space', ' ')
    NUMBER      = defGrammar('number', '[+-]?[0-9]+\.?[0-9]*')
    STRINGS     = defGrammar('strings', '[a-zA-Zぁ-んァ-ン一-龥：-＠]*')
    SYMBOLS     = defGrammar('symbols', '[!-/:-@[-`{-~]')
    
    @classmethod
    def sequence(cls, *grammars, isConv=False, isSkip=False) -> Callable:
        # sequence: e1 e2
        @wraps(cls.sequence)
        def _parser(src: str, ast: list, isSkip=isSkip):
            _ast = []
            for gram in grammars:
                _r, _s = gram(src, _ast, isSkip) if isSkip else gram(src, _ast)
                if _r: src = _s
                else: break
            if _ast and len(_ast) > 0:
                ast.append((name, _reduceListVals(_ast) if isConv else _ast))
            if src:
                return True, src
            return False, src
        return _parser
    
    @classmethod
    def ordered(cls, *grammars, isConv=False, isSkip=False) -> Callable:
        # ordered choice: e1/e2
        @wraps(cls.ordered)
        def _parser(src: str, ast: list, isSkip=isSkip):
            _ast = []
            for gram in grammars:
                _r, _s = gram(src, _ast, isSkip) if isSkip else gram(src, _ast)
                if _r:
                    src = _s
                    break
            if _ast and len(_ast) > 0:
                ast.append((name, _reduceListVals(_ast) if isConv else _ast))
            if src:
                return True, src
            return False, src
        return _parser
    
    @classmethod
    def zeroOrMore(cls, grammar, isConv=False, isSkip=False) -> Callable:
        # zero or more: e1*
        @wraps(cls.zeroOrMore)
        def _parser(src: str, ast: list, isSkip=isSkip):
            _ast = []
            while True:
                _r, _s = grammar(src, _ast, isSkip) if isSkip else grammar(src, _ast)
                if _r:
                    src = _s
                else:
                    break
            if _ast and len(_ast) > 0:
                ast.append((name, _reduceListVals(_ast) if isConv else _ast))
            if src:
                return True, src
            return False, src
        return _parser
    
    @classmethod
    def oneOrMore(cls, grammar, isConv=False, isSkip=False) -> Callable:
        # one ore more: e1+
        @wraps(cls.oneOrMore)
        def _parser(src: str, ast: list, isSkip=isSkip):
            _ast = []
            _r, _s = grammar(src, _ast, isSkip) if isSkip else grammar(src, _ast)
            if _r:
                src = _s
                while True:
                    _r, _s = grammar(src, _ast, isSkip) if isSkip else grammar(src, _ast)
                    if _r:
                        src = _s
                    else:
                        break
            else:
                return False, src
            if _ast and len(_ast) > 0:
                ast.append((name, _reduceListVals(_ast) if isConv else _ast))
            if src:
                return True, src
            return False, src
        return _parser
        
    @classmethod
    def optional(cls, grammar, isConv=False, isSkip=False) -> Callable:
        # optional: e1?
        @wraps(cls.optional)
        def _parser(src: str, ast: list, isSkip=isSkip):
            _ast = []
            _r, _s = grammar(src, _ast, isSkip) if isSkip else grammar(src, _ast)
            if _r:
                src = _s
                if _ast and len(_ast) > 0:
                    ast.append((name, _reduceListVals(_ast) if isConv else _ast))
            return True, src
        return _parser
        
    @classmethod
    def andPred(cls, grammar, isConv=False, isSkip=False) -> Callable:
        # and predicate: &e1
        @wraps(cls.andPred)
        def _parser(src: str, ast: list, isSkip=isSkip):
            _r, _s = grammar(src, _ast, isSkip) if isSkip else grammar(src, _ast)
            return _r, src
        return _parser
        
    @classmethod
    def notPred(cls, *grammars, isConv=False, isSkip=False) -> Callable:
        # not predicate: !e1
        @wraps(cls.notPred)
        def _parser(src: str, ast: list, isSkip=isSkip):
            _r, _s = grammar(src, _ast, isSkip) if isSkip else grammar(src, _ast)
            return not _r, src
        return _parser
        
    @classmethod
    def parse(cls, src: str, grammars: list, ast: list) -> bool:
        _src = src
        if isfunction(grammars):
            return grammars(src, ast) == ''
        for gram in grammars:
            _r, _s = gram(_src, ast)
            if not _r or _s == '': return True
            _src = _s
        return False
            
