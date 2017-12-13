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
MatchResult = NewType('MatchResult', Union[str, None])

DEFAULT_NAME = '__undefined__'

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
    exprs(pattern, list[Term, NTerm]): expressions
    attr(TermAttr): term attributes
    shorted(bool): is shorted values flag
'''
NTerm = namedtuple('NTerm', 'name exprs attr shorted')

''' Ast node:

    name: (str) symbol name
    val: (list) node values
'''
AstNode = namedtuple('AstNode', 'name val')# Node val must be list type.

_EmptyNode = AstNode('__empty__', None)

EmptyExpr = namedtuple('EmptyExpr', 'match')

EMPTY       = Term(EmptyExpr(lambda s: (True, s)))
WHITESPACE  = NTerm('__space__', [Term(re.compile('[\s\t]'))], TermAttr.SEQUENCE, True)
ENDLINE     = NTerm('__endline__', [Term(re.compile('\n'))], TermAttr.SEQUENCE, True)
SYMBOLS     = NTerm('__symbol__', [Term(re.compile('[!-/:-@[-`{-~]'))], TermAttr.SEQUENCE, True)
STRINGS     = NTerm('__string__', [Term(re.compile('[a-zA-Zぁ-んァ-ン一-龥：-＠]+'))], TermAttr.SEQUENCE, True)
NUMBERS     = NTerm('__number__', [Term(re.compile('[+-]?[0-9]+\.?[0-9]*'))], TermAttr.SEQUENCE, True)

EndTerms = (WHITESPACE, ENDLINE, SYMBOLS, STRINGS, NUMBERS)

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
def _toTerm(pattern: str) -> Term: return Term(re.compile(pattern))

def _createNTermExpr(exprs: tuple) -> Union[Term, list]:
    return len(exprs) == 1 and isinstance(exprs[0], str) and _toTerm(exprs[0]) \
        or [_toTerm(e) if isinstance(e, str) else e for e in exprs if isinstance(e, (str, NTerm))]

def _createNTerm(name: str, *exprs: Union[str, list], attr: TermAttr=TermAttr.SEQUENCE, shorted: bool=True) -> NTerm:
    return NTerm(name, _createNTermExpr(exprs), attr, shorted)

def _expression(src: str, term: Term): return term.pattern.match(src)

def _invalidTerm(t: Any) -> bool:
    return not isinstance(t, Term)

def _invalidNTerm(t: Any) -> bool:
    return not isinstance(t, NTerm)

def _invalidList(t: Any) -> bool:
    return not isinstance(t, list)

def _nodesReduced(nodes: list, shorted: bool=True) -> list:
    _conv = []
    _tmp = ''
    _hasAst = False
    for node in nodes:
        if isinstance(node, str): _tmp += node
        else:# astnode
            if _tmp != '':
                _conv.append(_tmp)
                _tmp = ''
            if node != _EmptyNode:
                _hasAst = True
                _conv.append(_nodesReduced(node.val, True) if shorted else node)
    if _tmp != '': _conv.append(_tmp)
    return _conv if not shorted and _hasAst else "".join(_conv)

def _parseTerm(src: str, terms: Term, attr: TermAttr=TermAttr.SEQUENCE) -> Tuple[str, MatchResult]:
    if _invalidTerm(terms): raise InvalidTermError
    _src = src
    if attr == TermAttr.ZERO_OR_MORE:
        _tmp = []
        while True:
            _m = _expression(_src, terms)
            if _m:
                _tmp.append(_m.group(0))
                _src = _src[len(str(_m.group(0))):]
            elif _src == '': break
            else: break
        return (_src, "".join(_nodesReduced(_tmp)) if len(_tmp) > 0 else _EmptyNode)
    elif attr == TermAttr.ONE_OR_MORE:
        _m = _expression(_src, terms)
        if not _m: return (_src, None)
        _tmp = [_m.group(0)]
        _src = _src[len(str(_m.group(0))):]
        while True:
            _m = _expression(_src, terms)
            if _m:
                _tmp.append(_m.group(0))
                _src = _src[len(str(_m.group(0))):]
            elif _src == '': break
            else: break
        return (_src, "".join(_nodesReduced(_tmp)))
    elif attr == TermAttr.OPTIONAL:
        _m = _expression(_src, terms)
        if not _m:
            return (src, _EmptyNode)
    elif attr == TermAttr.AND_PRED:
        _m = _expression(_src, terms)
        if _m:
            return (src, _EmptyNode)
        else:
            return (src, None)
    elif attr == TermAttr.NOT_PRED:
        _m = _expression(_src, terms)
        if not _m:
            return (src, _EmptyNode)
        else:
            return (src, None)
    else:
        _m = _expression(_src, terms)
    return _m and (_src[len(str(_m.group(0))):], _m.group(0)) or (_src, None)

def _parseNTerm(src: str, terms: NTerm) -> Tuple[str, Union[dict, str]]:
    if _invalidNTerm(terms): raise InvalidNonTermError
    return _parse(src, terms.exprs, terms.name, terms.attr, terms.shorted)

def _parseList(src: str, terms: list, name: str, attr: TermAttr=TermAttr.SEQUENCE, shorted: bool=True) -> Tuple[str, list]:
    if _invalidList(terms): raise InvalidNonTermValueError
    _nodes = []
    _src = src
    for t in terms:
        _s, _res = _parse(_src, t, name, attr)
        if attr == TermAttr.ORDERED:
            if _res:
                _nodes.append(_res)
                _src = _s
                break
        else:# Sequence
            if _res:
                _nodes.append(_res)
                _src = _s
            else:
                break
    return (attr == TermAttr.AND_PRED or attr == TermAttr.NOT_PRED) and (src, _EmptyNode) \
        or (_src, _nodesReduced(_nodes, shorted))

def _parse(src, terms, name, attr: TermAttr=TermAttr.SEQUENCE, shorted: bool=True) -> Tuple[str, Union[dict, str]]:
    if isinstance(terms, Term):
        _src, _res = _parseTerm(src, terms, attr)
        return (_src, _res)
    elif isinstance(terms, NTerm):
        _src, _res = _parseNTerm(src, terms)
        return (_src, _res if _res else None)
    elif isinstance(terms, list):
        _src, _res = _parseList(src, terms, name, attr, shorted)
        return (_src, AstNode(name, _res) if _res else None)
    else:
        raise InvalidGrammarError

# #################################################################### #
#   PEG class
# #################################################################### #
class PEG(object):
    
    _symbols = {}
    
    WHITESPACE  = WHITESPACE
    ENDLINE     = ENDLINE
    SYMBOLS     = SYMBOLS
    STRINGS     = STRINGS
    NUMBERS     = NUMBERS
    
    @classmethod
    def _invalidateGrammar(cls, grammar: Any) -> bool: return not isinstance(grammar, NTerm)
    
    @classmethod
    def _invalidateSymbol(cls, symbolName: str) -> bool: return symbolName in cls._symbols
    
    @classmethod
    def _validateSymbol(cls, symbolName: str) -> bool: return not symbolName in cls._symbols
    
    @classmethod
    def _appendSymbol(cls, name: str, term: NTerm) -> NTerm:
        if name == DEFAULT_NAME: name = str(id(term))
        if cls._invalidateSymbol(name): raise InvalidSymbolError
        else: return (cls._symbols.update({name: term}) or term)
    
    @classmethod
    def grammar(cls, name: str, *exprs, shorted: bool=False, attr: TermAttr=TermAttr.SEQUENCE) -> NTerm:
        return cls._appendSymbol(name, _createNTerm(name, *exprs, attr=attr, shorted=shorted))
    
    @classmethod
    def ordered(cls, *exprs, shorted: bool=True) -> NTerm:
        return cls.grammar(DEFAULT_NAME, *exprs, shorted=shorted, attr=TermAttr.ORDERED)

    @classmethod
    def zeroMore(cls, *exprs, shorted: bool=True) -> NTerm:
        return cls.grammar(DEFAULT_NAME, *exprs, shorted=shorted, attr=TermAttr.ZERO_OR_MORE)
        
    @classmethod
    def oneMore(cls, *exprs, shorted: bool=True) -> NTerm:
        return cls.grammar(DEFAULT_NAME, *exprs, shorted=shorted, attr=TermAttr.ONE_OR_MORE)
        
    @classmethod
    def optional(cls, *exprs, shorted: bool=True) -> NTerm:
        return cls.grammar(DEFAULT_NAME, *exprs, shorted=shorted, attr=TermAttr.OPTIONAL)
    
    @classmethod
    def andPred(cls, *exprs, shorted: bool=True) -> NTerm:
        return cls.grammar(DEFAULT_NAME, *exprs, shorted=shorted, attr=TermAttr.AND_PRED)
        
    @classmethod
    def notPred(cls, *exprs, shorted: bool=True) -> NTerm:
        return cls.grammar(DEFAULT_NAME, *exprs, shorted=shorted, attr=TermAttr.NOT_PRED)
        
    @classmethod
    def parse(cls, src: str, grammar: NTerm) -> tuple:
        if cls._invalidateGrammar(grammar): raise InvalidGrammarError
        _src, _res = _parse(src, grammar, grammar.name, grammar.attr)
        return _src, _res if isinstance(_res, AstNode) else AstNode(grammar.name, _res)
