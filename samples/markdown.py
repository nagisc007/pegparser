#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2017 N.T.WORKS Authors. All Rights Reserved.
#
#      http://opensource.org/licenses/mit-license.php
#

""" Sample file: Case of Markdown
"""

# #### Imports ####################################################### #
# Builtin
import os
import sys
# PEG package
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
from pegparser import PEG

# #### Sample source ################################################# #
SAMPLE_MARKDOWN = """# Document Title

## Sub title

### Headline

Sample markdown。

- li1
- li2
* li3
* li4

1. ol1
2. ol2

> これ引用です

<!-- これコメントな -->

---
***
強調も**含んだ文章**です

End.

"""

# #### Tests ######################################################### #

def main(argv: list) -> int:
    # define grammars
    STR_WS      = PEG.grammar(None, PEG.oneMore(PEG.ordered(PEG.STRING_JP, PEG.NUMBER, PEG.WS, '\.')))
    Head1       = PEG.grammar('head1', '# .', STR_WS)
    Head2       = PEG.grammar('head2', '## .', STR_WS)
    Head3       = PEG.grammar('head3', '### .', STR_WS)
    List1       = PEG.grammar('list1', '[\-\*] .', STR_WS)
    List2       = PEG.grammar('list2', PEG.NUMBER, '\. ', STR_WS)
    QUOTE       = PEG.grammar('quote', '> .', STR_WS)
    EMB         = PEG.grammar('embed', '[\_\*]{2}', PEG.oneMore(STR_WS) ,'[\_\*]{2}')
    PARAGRAPH   = PEG.grammar("parag", PEG.oneMore(PEG.ordered(STR_WS, EMB)), PEG.optional(PEG.BR))
    HR          = PEG.grammar('hr', '---+|\*\*\*+')
    COMMENT     = PEG.grammar('comment', '<!--', PEG.zeroMore(PEG.ordered(STR_WS, PEG.BR)), '-->')
    Markdown    = PEG.grammar("Markdown", PEG.oneMore(PEG.ordered(Head1, Head2, Head3, List1, List2, QUOTE, HR, COMMENT, PARAGRAPH,PEG.BR)))
    
    # parse source
    res = PEG.parse(SAMPLE_MARKDOWN, Markdown, excepted='\n')
    
    print("Parse result: ",res)
    
    return 0

# #### main ########################################################## #
if __name__ == '__main__':
    main(sys.argv)
