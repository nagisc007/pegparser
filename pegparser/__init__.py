#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2017 N.T.WORKS Authors. All Rights Reserved.
#
#      http://opensource.org/licenses/mit-license.php
#

''' Note:

    Terminal symbol:    literal (numbers, strings, symbols)
    Non-terminal symbol:Alphabet to define
    Empty character:    white spaces(contains tab, break-line)
'''

# #### Imports ####################################################### #
from collections import namedtuple
from enum import Enum
import re
from typing import Any
from typing import Callable
from typing import Tuple
from typing import Union
from typing import NewType
from typing.re import Pattern
# #### Defines ####################################################### #
# Types
MatchResult = NewType('MatchResult', Union[str, None])

# Enums
class BaseSymbol(Enum):
    UNDEF       = '__undefined__'
    EMPTY       = '__empty__'
    WHITESPACE  = '__space__'
    SYMBOL      = '__symbol__'
    STRING      = '__string__'
    STRING_JP   = '__stringjp__'
    NUMBER      = '__number__'
    ENDLINE     = '__endline__'
    ENDMARK     = '__endmark__'

class TermAttr(Enum):
    SEQUENCE    = 1
    ORDERED     = 2
    ZERO_OR_MORE= 3
    ONE_OR_MORE = 4
    OPTIONAL    = 5
    AND_PRED    = 6
    NOT_PRED    = 7

'''Terminal symbol:
    pattern(Pattern): the pattern compiled for matching any.
'''
Term = namedtuple('Term', 'pattern')

'''Non-Terminal symbol:
    name(str): symbol name
    exprs(list[Term, NTerm]): expressions
    attr(TermAttr): term attributes
'''
NTerm = namedtuple('NTerm', 'name exprs attr')

'''Node: AST node

    name: (str) symbol name
    val: (list) node values
'''
Node = namedtuple('Node', 'name val')# Node val must be list type.

_EmptyNode = Node('__empty__', None)

EmptyExpr = namedtuple('EmptyExpr', 'match')

EMPTY       = Term(EmptyExpr(lambda s: (True, s)))
WHITESPACE  = NTerm(BaseSymbol.EMPTY.value, [Term(re.compile('[ \t]'))], TermAttr.SEQUENCE)
ENDLINE     = NTerm(BaseSymbol.ENDLINE.value, [Term(re.compile('\n'))], TermAttr.SEQUENCE)
SYMBOL      = NTerm(BaseSymbol.SYMBOL.value, [Term(re.compile('[!-/:-@[-`{-~]*(?=\n).+'))], TermAttr.SEQUENCE)
STRING      = NTerm(BaseSymbol.STRING.value, [Term(re.compile('[a-zA-Z\.\,]+$'))], TermAttr.SEQUENCE)
STRING_JP   = NTerm(BaseSymbol.STRING_JP.value, [Term(re.compile('[a-zA-Zぁ-んァ-ン一-龥：-＠。、]+'))], TermAttr.SEQUENCE)
NUMBER      = NTerm(BaseSymbol.NUMBER.value, [Term(re.compile('[+-]?[0-9]+\.?[0-9]*'))], TermAttr.SEQUENCE)

class InvalidGrammarError(Exception):
    '''Raised when invalid grammar.'''

class InvalidGrammarValueError(Exception):
    '''Raised when invalid value to use grammar.'''

class InvalidSymbolError(Exception):
    '''Raised when invalid symbol name.'''

class InvalidTermError(Exception):
    '''Raised when invalid terminal symbol.'''

class InvalidNonTermError(Exception):
    '''Raised when invalid non-terminal symbol.'''

class InvalidNonTermValueError(Exception):
    '''Raised when invalid non-terminal symbol value.'''

class InvalidExpressionError(Exception):
    '''Raised when invalid non-terminal symbol expression.'''

# #### Functions ##################################################### #
_baseNodeNames = [x.value for x in list(BaseSymbol)]

def _isBaseNode(node: Node) -> bool: return node.name in _baseNodeNames

def _termFrom(pattern: str) -> Term: return Term(re.compile(pattern))

def _nonTermExprFrom(src: tuple) -> list:
    return len(src) == 1 and isinstance(src[0], str) and [_termFrom(src[0])] \
        or [_termFrom(s) if isinstance(s, str) else s for s in src if isinstance(s, (str, NTerm))]

def _nonTermFrom(name: str, *exprs: Union[str, NTerm], attr: TermAttr=TermAttr.SEQUENCE) -> NTerm:
    return NTerm(name, _nonTermExprFrom(exprs), attr)

def _exprTerm(src: str, t: Term):
    _m = t.pattern.match(src)
    return _m

def _expression(src: str, t: Union[Term, NTerm]):
    if isinstance(t, Term):
        _m = _exprTerm(src, t)
        return _m and (src[len(str(_m.group(0))):], _m.group(0)) or (src, None)
    elif isinstance(t, NTerm): return _parse(src, t)
    else: raise InvalidGrammarError

def _isSuccess(attr: TermAttr, e: Any) -> bool:
    if attr in (TermAttr.NOT_PRED,):
        return e is None
    return not e is None

def _parse(src: str, grammar: NTerm, excepted=None) -> Tuple[str, MatchResult]:
    _src = src
    _nodes = []
    _len = len(src)
    for e in grammar.exprs:
        _s, _m = _expression(_src, e)
        if grammar.attr == TermAttr.SEQUENCE:
            if _isSuccess(grammar.attr, _m):
                _nodes.append(_m)
                _src = _s
            else: break
        elif grammar.attr == TermAttr.ORDERED:
            if _isSuccess(grammar.attr, _m):
                _nodes.append(_m)
                _src = _s
                break
        elif grammar.attr == TermAttr.ZERO_OR_MORE:
            if not _isSuccess(grammar.attr, _m): continue
            _nodes.append(_m)
            _src = _s
            while True:
                _s, _m = _expression(_src, e)
                if _isSuccess(grammar.attr, _m):
                    _nodes.append(_m)
                    _src = _s
                else: break
                if _src == '': break
        elif grammar.attr == TermAttr.ONE_OR_MORE:
            if _isSuccess(grammar.attr, _m):
                _nodes.append(_m)
                _src = _s
            else: break
            while True:
                _s, _m = _expression(_src, e)
                if _isSuccess(grammar.attr, _m):
                    _nodes.append(_m)
                    _src = _s
                else: break
                if _src == '': break
        elif grammar.attr == TermAttr.OPTIONAL:
            if _isSuccess(grammar.attr, _m):
                _nodes.append(_m)
                _src = _s
        elif grammar.attr == TermAttr.AND_PRED:
            if not _isSuccess(grammar.attr, _m): break
        elif grammar.attr == TermAttr.NOT_PRED:
            if not _isSuccess(grammar.attr, _m): break
        else:# sequence
            if _isSuccess(grammar.attr, _m):
                _nodes.append(_m)
                _src = _s
            else: break
        if _src == '': break
    return len(_nodes) == 0 and (_src, [] if grammar.attr == TermAttr.ZERO_OR_MORE else None) \
        or (_src, _nodesReduced(_nodes, excepted) if _isBaseNode(grammar) else Node(grammar.name, _nodesReduced(_nodes, excepted)))

def _nodesReduced(nodes: list, excepted=None) -> Union[list, Node, str]:
    _nodes = []
    _tmp = ''
    _hasNode = False
    for n in nodes:
        if isinstance(n, str):
            if not excepted is None and re.match(excepted, n): continue
            _tmp += n
        elif isinstance(n, Node):
            if _tmp:
                _nodes.append(_tmp)
                _tmp = ''
            _hasNode = True
            _nodes.append(n)
        elif isinstance(n, list):
            _res = _nodesReduced(n, excepted)
            if isinstance(_res, str): _tmp += _res
            else:
                _hasNode = True
                _nodes.append(_res)
    if _tmp:
        _nodes.append(_tmp)
    return _nodes if _hasNode else "".join(_nodes)

# #################################################################### #
#   PEG class
# #################################################################### #
class PEG(object):
    
    _symbols = {}
    
    UNDEF       = BaseSymbol.UNDEF.value
    #
    BR          = ENDLINE
    EMPTY       = EMPTY
    ENDLINE     = ENDLINE
    NUMBER      = NUMBER
    STRING      = STRING
    STRING_JP   = STRING_JP
    SYMBOL      = SYMBOL
    WHITESPACE  = WHITESPACE
    WS          = WHITESPACE
    
    @classmethod
    def grammar(cls, name: Union[str, None], *exprs: Union[str, NTerm], attr: TermAttr=TermAttr.SEQUENCE) -> NTerm:
        return _nonTermFrom(name if name else BaseSymbol.UNDEF.value, *exprs, attr=attr)
    
    @classmethod
    def ordered(cls, *exprs) -> NTerm:
        return cls.grammar(None, *exprs, attr=TermAttr.ORDERED)
    
    @classmethod
    def zeroMore(cls, *exprs) -> NTerm:
        return cls.grammar(None, *exprs, attr=TermAttr.ZERO_OR_MORE)
    
    @classmethod
    def oneMore(cls, *exprs) -> NTerm:
        return cls.grammar(None, *exprs, attr=TermAttr.ONE_OR_MORE)
    
    @classmethod
    def optional(cls, *exprs) -> NTerm:
        return cls.grammar(None, *exprs, attr=TermAttr.OPTIONAL)
    
    @classmethod
    def andPred(cls, *exprs) -> NTerm:
        return cls.grammar(None, *exprs, attr=TermAttr.AND_PRED)
    
    @classmethod
    def notPred(cls, *exprs) -> NTerm:
        return cls.grammar(None, *exprs, attr=TermAttr.NOT_PRED)
    
    @classmethod
    def parse(cls, src: str, grammar: NTerm, excepted=None) -> tuple:
        return _parse(src, grammar, excepted)
