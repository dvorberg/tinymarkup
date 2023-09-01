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


import html, copy, dataclasses, re

import ply.lex

from .exceptions import Location

def html_start_tag(tag, **params):
    def fixkey(key):
        if key.endswith("_"):
            key = key[:-1]

        return key.replace("_", "-")

    if params:
        params = [ f'{fixkey(key)}="{html.escape(value)}"'
                   for (key, value) in params.items() ]
        params = " " + " ".join(params)
    else:
        params = ""

    return f"<{tag}{params}>"


def get_remainder(lexer:ply.lex.Lexer) -> str:
    return lexer.lexdata[lexer.lexpos:]

def set_remainder(lexer:ply.lex.Lexer, remainder:str):
    if not lexer.lexoptimize:
        assert lexer.lexdata.endswith(remainder)

    lexer.lexpos = len(lexer.lexdata)-len(remainder)

def get_location(lexer:ply.lex.Lexer) -> Location:
    return Location.from_baselexer(lexer)

param_re = re.compile(r'([-a-zA-Z]+)=(?:(?:\'([^\']*))|(?:\"([^\"]*)\"))')
def parse_tag_params(params):
    if not params:
        return {}

    return dict([ (name, single or double,)
                  for (name, single, double)
                    in param_re.findall(params) ])
