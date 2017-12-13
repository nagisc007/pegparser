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

Sample markdown.
"""

# #### Tests ######################################################### #

def main(argv: list) -> int:
    # define grammars
    Head1       = PEG.grammar("head1", '# [a-zA-Zぁ-んァ-ン一-龥：-＠].*', PEG.BR)
    Head2       = PEG.grammar("head2", '## [a-zA-Zぁ-んァ-ン一-龥：-＠].*', PEG.BR)
    Head3       = PEG.grammar("head3", '### [a-zA-Zぁ-んァ-ン一-龥：-＠].*', PEG.BR)
    PARAGRAPH   = PEG.grammar("parag", PEG.STRINGS, PEG.BR, isSkip=True)
    Markdown    = PEG.grammar("Markdown", PEG.ordered("Markdown", Head1,Head2, Head3, PARAGRAPH,PEG.BR), '+')
    
    # parse source
    ast = []
    res = PEG.parse(SAMPLE_MARKDOWN, Markdown, ast)
    
    print("Parse result: ",res)
    print("AST is:\n", ast)
    
    return 0

# #### main ########################################################## #
if __name__ == '__main__':
    main(sys.argv)
