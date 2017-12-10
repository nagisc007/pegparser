#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2017 N.T.WORKS Authors. All Rights Reserved.
#
#      http://opensource.org/licenses/mit-license.php
#

# #### Imports ####################################################### #
from collections import namedtuple
from functools import wraps
from inspect import isfunction
import re
from typing import Callable
from typing import Union

# #### Defines ####################################################### #
PegGrammar = namedtuple('PegGrammar', 'name parse')
AstNode = namedtuple('AstNode', 'name val')

class InvalidGrammarError(Exception):
    '''Raised when invalid grammar.'''

# #### Functions ##################################################### #
def _skipSpace(src: str, isSkip: bool=False) -> str: return isSkip and src.lstrip() or src

def _reduceListVals(src) -> str:
    def _toStr(s):
        if isinstance(s, str): return s
        if isinstance(s, AstNode):
            return s.val
        elif isinstance(s, list):
            return "".join([_toStr(x) for x in s])
        else:
            return ""
    return _toStr(src)

# #################################################################### #
#   PEG class
# #################################################################### #
class PEG(object):
    
    @classmethod
    def _appendAstNode(cls, name: str, origin: list, src: Union[list, str, None], isConv: bool) -> bool:
        if src and (isinstance(src, (list,tuple)) and len(src) > 0 or isinstance(src, str)):
            origin.append(AstNode(name, _reduceListVals(src) if isConv else src))
            return True
        return False
    
    @classmethod
    def sequence(cls, name: str, *grammars: PegGrammar, isConv=False, isSkip=False) -> PegGrammar:
        # sequence: e1 e2
        @wraps(cls.sequence)
        def _parser(src: str, ast: list, isSkip=isSkip):
            _ast = []
            for gram in grammars:
                _r, _s = gram.parse(src, _ast, isSkip) if isSkip else gram.parse(src, _ast)
                if _r: src = _s
                else: break
            cls._appendAstNode(name, ast, _ast, isConv)
            if src:
                return True, src
            return False, src
        return PegGrammar(name, _parser)
    
    @classmethod
    def ordered(cls, name: str, *grammars: PegGrammar, isConv=False, isSkip=False) -> PegGrammar:
        # ordered choice: e1/e2
        @wraps(cls.ordered)
        def _parser(src: str, ast: list, isSkip=isSkip):
            _ast = []
            for gram in grammars:
                _r, _s = gram.parse(src, _ast, isSkip) if isSkip else gram.parse(src, _ast)
                if _r:
                    src = _s
                    break
            cls._appendAstNode(name, ast, _ast, isConv)
            if src:
                return True, src
            return False, src
        return PegGrammar(name, _parser)
    
    @classmethod
    def zeroOrMore(cls, name: str, grammar: PegGrammar, isConv=False, isSkip=False) -> PegGrammar:
        # zero or more: e1*
        @wraps(cls.zeroOrMore)
        def _parser(src: str, ast: list, isSkip=isSkip):
            _ast = []
            while True:
                _r, _s = grammar.parse(src, _ast, isSkip) if isSkip else grammar.parse(src, _ast)
                if _r:
                    src = _s
                else:
                    break
            cls._appendAstNode(name, ast, _ast, isConv)
            if src:
                return True, src
            return False, src
        return PegGrammar(name, _parser)
    
    @classmethod
    def oneOrMore(cls, name: str, grammar: PegGrammar, isConv=False, isSkip=False) -> PegGrammar:
        # one ore more: e1+
        @wraps(cls.oneOrMore)
        def _parser(src: str, ast: list, isSkip=isSkip):
            _ast = []
            _r, _s = grammar.parse(src, _ast, isSkip) if isSkip else grammar.parse(src, _ast)
            if _r:
                src = _s
                while True:
                    _r, _s = grammar.parse(src, _ast, isSkip) if isSkip else grammar.parse(src, _ast)
                    if _r:
                        src = _s
                    else:
                        break
            else:
                return False, src
            cls._appendAstNode(name, ast, _ast, isConv)
            if src:
                return True, src
            return False, src
        return PegGrammar(name, _parser)
        
    @classmethod
    def optional(cls, name: str, grammar: PegGrammar, isConv=False, isSkip=False) -> PegGrammar:
        # optional: e1?
        @wraps(cls.optional)
        def _parser(src: str, ast: list, isSkip=isSkip):
            _ast = []
            _r, _s = grammar.parse(src, _ast, isSkip) if isSkip else grammar.parse(src, _ast)
            if _r:
                src = _s
                cls._appendAstNode(name, ast, _ast, isConv)
            return True, src
        return PegGrammar(name, _parser)
        
    @classmethod
    def andPred(cls, name: str, grammar: PegGrammar, isSkip=False) -> PegGrammar:
        # and predicate: &e1
        @wraps(cls.andPred)
        def _parser(src: str, ast: list, isSkip=isSkip):
            _r, _s = grammar.parse(src, None, isSkip) if isSkip else grammar.parse(src, None)
            return _r, src
        return PegGrammar(name, _parser)
        
    @classmethod
    def notPred(cls, name: str, grammar: PegGrammar, isSkip=False) -> PegGrammar:
        # not predicate: !e1
        @wraps(cls.notPred)
        def _parser(src: str, ast: list, isSkip=isSkip):
            _r, _s = grammar.parse(src, None, isSkip) if isSkip else grammar.parse(src, None)
            return not _r, src
        return PegGrammar(name, _parser)
    
    @classmethod
    def grammar(cls, name: str, *srcs: Union[str, PegGrammar], isSkip=False) -> PegGrammar:
        _grams = []
        _tmp = None
        _isOrdered = None
        for src in srcs:
            if _isOrdered:
                if _isOrdered == '/' and _tmp:
                    _grams.append(cls.ordered(name, _tmp, cls._grammar(name, src, isSkip=isSkip), isConv=True, isSkip=isSkip))
                elif _isOrdered == '&':
                    _grams.append(cls.andPred(name, cls._grammar(name, src, isSkip=isSkip), isSkip=isSkip))
                elif _isOrdered == '!':
                    _grams.append(cls.notPred(name, cls._grammar(name, src, isSkip=isSkip), isSkip=isSkip))
                _isOrdered = None
                _tmp = None
            elif isinstance(src, str):
                if src == '/' and _tmp:
                    _isOrdered = src
                elif src in ('&', '!'):
                    _isOrdered = src
                    if _tmp:
                        _grams.append(_tmp)
                        _tmp = None
                elif src == '*' and _tmp:
                    _grams.append(cls.zeroOrMore(name, _tmp, isConv=True, isSkip=isSkip))
                    _tmp = None
                elif src == '+' and _tmp:
                    _grams.append(cls.oneOrMore(name, _tmp, isConv=True, isSkip=isSkip))
                    _tmp = None
                elif src == '?' and _tmp:
                    _grams.append(cls.optional(name, _tmp, isConv=True, isSkip=isSkip))
                    _tmp = None
                else:
                    if _tmp:
                        _grams.append(_tmp)
                        _tmp = cls._grammar(name, src, isSkip=isSkip)
                    else:
                        _tmp = cls._grammar(name, src, isSkip=isSkip)
            elif isinstance(src, PegGrammar):
                _grams.append(src)
            else:
                raise InvalidGrammarError
        if _tmp:
            _grams.append(_tmp)
        return len(_grams) == 1 and _grams[0] \
            or cls.sequence(name, *_grams, isConv=True, isSkip=isSkip)
    
    @classmethod
    def _grammar(cls, name: str, pattern: str, isSkip: bool=False) -> PegGrammar:
        _compiled = re.compile(pattern)
        def _parser(src: str, ast: list, isSkip=isSkip):
            src = _skipSpace(src, isSkip)
            _m = _compiled.match(src)
            if _m:
                if not ast is None:
                    cls._appendAstNode(name, ast, _m.group(0), False)
                return True, src[len(str(_m.group(0))):]
            return False, src
        return PegGrammar(name, _parser)
    
    @classmethod
    def parse(cls, src: str, grammars: Union[PegGrammar, list], ast: list) -> bool:
        _src = src
        if isinstance(grammars, PegGrammar):
            _r, _s = grammars.parse(src, ast)
            return  _r or _s == ''
        for gram in grammars:
            if not isinstance(gram, PegGrammar):
                raise InvalidGrammarError
            _r, _s = gram.parse(_src, ast)
            if not _r or _s == '': return True
            _src = _s
        return False

# basic grammar implemented
PEG.BR          = PEG._grammar('breakline', '\n')
PEG.SPACE       = PEG._grammar('space', '\s')
PEG.NUMBER      = PEG._grammar('number', '[+-]?[0-9]+\.?[0-9]*')
PEG.STRINGS     = PEG._grammar('strings', '[a-zA-Zぁ-んァ-ン一-龥：-＠]+')
PEG.SYMBOLS     = PEG._grammar('symbols', '[!-/:-@[-`{-~]')

# shorter
PEG.seq = PEG.sequence
PEG.o = PEG.ordered
PEG.one = PEG.oneOrMore
PEG.opt = PEG.optional
PEG.zero = PEG.zeroOrMore
PEG.a = PEG.andPred
PEG.n = PEG.notPred
