# Copyright (C) 2023 Diedrich Vorberg
#
# Contact: diedrich@tux4web.de
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

import copy

import ply.lex

from .exceptions import Location
from .utils import get_remainder, set_remainder

class Parser(object):
    def __init__(self, baselexer:ply.lex.Lexer):
        self.lexer = LexerWrapper(baselexer)

    @property
    def location(self) -> Location:
        return self.lexer.location

class LexerWrapper(object):
    """
    Prettify some of ply.lex.lex()’s functionality.
    """
    def __init__(self, lexer:ply.lex.Lexer):
        self.base = copy.copy(lexer)

    def tokenize(self, source:str):
        self._source = source
        self.base.input(source.lstrip())

        while True:
            token = self.base.token()
            if not token:
                break
            else:
                yield token

    @property
    def location(self) -> Location:
        return Location.from_baselexer(self.base)

    @property
    def remainder(self) -> str:
        return get_remainder(self.base)

    @property
    def lexpos(self) -> int:
        return self.base.lexpos

    @lexpos.setter
    def lexpos(self, lexpos:int):
        self.base.lexpos = lexpos

    @remainder.setter
    def remainder(self, remainder:str):
        set_remainder(self.base, remainder)

    @property
    def lexmatch(self):
        return self.base.lexmatch
