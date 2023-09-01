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

import dataclasses

from .context import Context
from .parser import Parser

class Compiler(object):
    def __init__(self, context:Context=None):
        if context is None:
            self.context = Context()
        else:
            self.context = context

    def compile(self, parser, source):
        parser.parse(source, self)

    def begin_document(self, parser:Parser):
        """
        Reset the internal datastructures to run a new document
        on the same context.
        """
        self.parser = parser

    def end_document(self):
        """
        Perform finishing tasks on internal datastructures
        before the compilation result may be retrieved.
        """
        pass

class CompilerDuplexer(object):
    """
    A CompilerDuplexer object acts as a stand-in for more than one
    compiler of the same superclass (i.e. implementing the same
    interface). Given 1…n compiler objects, this class will act as a
    proxy. Any method called on it will be forwarded to methods by the
    same name on the managed compilers.
    """
    def __init__(self, *compilers):
        """
        This is the constructor, implemented as classmethod because if
        there is only one compiler, it will just return it. Compilers may
        be None.
        """
        self._compilers = [ c for c in compilers if c is not None ]

    def duplex(self, parser, source):
        parser.parse(source, self)

    def __getattr__(self, name):
        return self.MethodProxy(self._compilers, name)

    @dataclasses.dataclass
    class MethodProxy(object):
        compilers: list
        method_name: str

        def __call__(self, *args, **kw):
            for compiler in self.compilers:
                method = getattr(compiler, self.method_name)
                method(*args, *kw)

        def __getattr__(self, name):
            return getattr(getattr(self.compilers[0], self.method_name), name)
