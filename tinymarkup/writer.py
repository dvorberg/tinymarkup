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

from html import escape as escape_html

from ll.xist import xsc

from .language import Language
from .exceptions import InternalError
from .utils import html_start_tag

class Writer(object):
    """
    Baseclass for writer objects that manage compiler output.
    """
    def __init__(self, output, root_language):
        self.output = output
        self.root_language = root_language

    def print(self, *args, **kw):
        print(*args, **kw, file=self.output)

class HTMLWriter(Writer):
    """
    HTMLCompiler output manager.
    """
    block_level_tags = { "div", "p", "ol", "ul", "li", "blockquote", "code",
                         "table", "tbody", "thead", "tr", "td", "th",
                         "dl", "dt", "dd",
                         "h1", "h2", "h3", "h4", "h5", "h6", }

    # Tags that like to stand on a line by themselves.
    loner_tags = { "div", "ol", "ul", "code",
                   "table", "tbody", "thead", "tr", "dl" }

    def __init__(self, output, root_language):
        super().__init__(output, root_language)
        self.tag_stack = []

    def print(self, *args, **kw):
        def convert(a):
            if isinstance(a, xsc.Node):
                return a.string()
            else:
                return a
        args = [ convert(arg) for arg in args if arg is not None ]
        print(*args, **kw, file=self.output)

    def open(self, tag, **params):
        # If we’re in a <p> and we’re opening a block level element,
        # close the <p> first.
        #if self.tag_stack and self.tag_stack[-1] == "p" \
        #   and tag in self.block_level_tags:
        #    self.close("p")
        if tag in self.loner_tags:
            end = "\n"
        else:
            end = ""

        self.print(html_start_tag(tag, **params), end=end)
        self.tag_stack.append(tag)

    def close(self, tag):
        if tag in self.block_level_tags:
            end = "\n"
        else:
            end = ""

        self.print(f"</{tag}>", end=end)

        if not self.tag_stack or self.tag_stack[-1] != tag:
            raise InternalError(f"Internal error. HTML nesting failed. "
                                f"Can’t close “{tag}”. "
                                f"Tag stack: {repr(self.tag_stack)}.",
                                location=self.parser.location)
        else:
            self.tag_stack.pop()

    def close_all(self):
        while self.tag_stack:
            self.close(self.tag_stack[-1])


class Write_setweight(object):
    def __init__(self, writer, weight):
        self.output = writer.output

        weight = weight.upper()
        assert len(weight) == 1 and weight in "ABCD", ValueError
        self._weight = weight

        self._to_tsvector_writer = None
        self._started = False

    def write(self, s:str, first_setweigt:bool):
        first = False
        if not self._started:
            if first_setweigt:
                self.output.write(" ||\n")

            if self.weight != "D":
                self.output.write("setweight(")

            self._started = True
            first = True

        self._to_tsvector_writer.write(s, first)

    def finish(self):
        self._to_tsvector_writer.finish()

        if self._started and self.weight != "D":
            self.output.write(f", '{self.weight}')")

    @property
    def tsvector_writer(self):
        raise NotImplementedError()

    @tsvector_writer.setter
    def tsvector_writer(self, writer):
        if self._to_tsvector_writer is not None:
            self._to_tsvector_writer.finish()
        self._to_tsvector_writer = writer

    @property
    def weight(self):
        return self._weight

    @property
    def language(self):
        if self._to_tsvector_writer is None:
            return None
        else:
            return self._to_tsvector_writer.language

class Write_tsvector(object):
    def __init__(self, writer, language):
        self.output = writer.output
        self._language = language
        self._started = False

    def write(self, s:str, first:bool):
        if not self._started:
            if not first:
                self.output.write(" ||\n")

            self.output.write(
                f"to_tsvector('{self.language.tsearch_configuration}', '")
            self._started = True
        else:
            self.output.write(" ")

        self.output.write(s.replace("'", "''"))

    def finish(self):
        if self._started:
            self.output.write("')")

    @property
    def language(self):
        return self._language


class TSearchWriter(Writer):
    def __init__(self, output, root_language):
        super().__init__(output, root_language)

        self.setweight_writer = None
        self.language_stack = [ self.root_language, ]
        self.weight_stack = [ "D", ]
        self._started = False

    def push_language(self, language):
        self.language_stack.append(language)

    def pop_language(self):
        self.language_stack.pop()
        if len(self.language_stack) == 0:
            raise InternalError("Can’t pop last language.")

    def push_weight(self, weight):
        self.weight_stack.append(weight)

    def pop_weight(self):
        self.weight_stack.pop()
        if len(self.weight_stack) == 0:
            raise InternalError("Can’t pop last weight.")

    def write(self, text:str, language:Language=None, weight="D"):
        if ( self.setweight_writer is not None
             and self.setweight_writer.weight != weight):
            self.setweight_writer.finish()
            self.setweight_writer = None

        if self.setweight_writer is None:
            self.setweight_writer = Write_setweight(self, weight)

        if language is None:
            language = self.root_language

        if self.setweight_writer.language != language:
            self.setweight_writer.tsvector_writer = Write_tsvector(
                self, language)

        self.setweight_writer.write(text, self._started)
        self._started = True

    def tsvector_break(self):
        """
        There is a limit in PostgreSQL’s to_tsvector() function. It will
        store positional information on lexemes only up to position 16383.
        Cf. https://www.postgresql.org/docs/current/datatype-textsearch.html
        This function will reset the Write_tsvector object to create a new
        call to ts_vector() in the output. Use the function after
        semantically defined breaks (end_paragraph() for example). The
        position information is used to identify matching phrases on
        search result weighting.
        """
        if self.setweight_writer is not None:
            self.setweight_writer.tsvector_writer = Write_tsvector(
                self, self.setweight_writer.language)

    def reset_to_root_language(self):
        while len(self.language_stack) > 1:
            self.language_stack.pop()

    def finish_tsearch(self):
        if self.setweight_writer is not None:
            self.setweight_writer.finish()
        self.setweight_writer = None

    # Default compiler methods can be implemented here as follows:
    def word(self, s:str):
        self.write(s, self.language_stack[-1], self.weight_stack[-1])

    def other_characters(self, s:str):
        """
        No need to add non-word characters to the full text input.
        """
        pass

    def end_document(self):
        self.finish_tsearch()
