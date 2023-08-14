"""
wikklytext.parser.py: Base parser interface to
wikklytext.lexer. Part of the WikklyText suite.

Copyright (C) 2007,2008 Frank McIngvale
Copyright (C) 2023 Diedrich Vorberg

Contact: diedrich@tux4web.de

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
"""


import dataclasses, io

@dataclasses.dataclass
class Location:
    lineno: int
    looking_at: str

    @classmethod
    def from_baselexer(cls, lexer):
        lineno = lexer.lexdata[:lexer.lexpos].count("\n") + 1
        remainder = lexer.lexdata[lexer.lexpos:]
        return Location( lineno = lineno,
                         looking_at = remainder[:40])

class MarkupError(Exception):
    """
	General-purpose exception raised when errors occur during parsing
	or XML/HTML generation.

	'message' is brief error message (no HTML)
	'looking_at' is text near/after error location
	'trace' is exception trace (raw text) , or '' if no exception occurred.
	'location' is buffer after point of error.
	"""
    def __init__(self, message:str, trace=None, location:Location=None):
        Exception.__init__(self, message)

        self.message = message
        self.trace = trace
        self.location = location

    @property
    def lineno(self):
        if self.location:
            return self.location.lineno
        else:
            return None

    @property
    def looking_at(self):
        if self.location:
            return self.location.looking_at
        else:
            return None

    def __str__(self):
        ret = io.StringIO()

        def say(*args):
            print(*args, end=" ", file=ret)

        say(f"{self.message}")
        if self.location:
            say(f"Line: {self.lineno}")
            say(f"Looking at: {repr(self.looking_at)}")

        if self.trace:
            say(f"Traceback: {self.trace}")

        return ret.getvalue()

class LexerSetupError(MarkupError):
    pass

class SyntaxError(MarkupError):
    pass

class ParseError(MarkupError):
    pass

class UnknownLanguage(MarkupError):
    pass

class InternalError(MarkupError):
    """
    There are a number of instances in which a programming errors
    might rather call this than create some unplaned condition that
    would be hard to debug.
    """
    pass

class ErrorInMacroCall(MarkupError):
    pass

class UnknownMacro(MarkupError):
    pass

class UnsuitableMacro(MarkupError):
    pass

class RestrictionError(MarkupError):
    pass
