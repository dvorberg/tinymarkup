# Copyright (C) 2023 Diedrich Vorberg

# Contact: diedrich@tux4web.de

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

from ll.xist.ns import html

from .exceptions import UnknownLanguage
from .language import Language, Languages
from .macro import MacroLibrary

## Context
class Context(object):
    def __init__(self,
                 macro_library:MacroLibrary=MacroLibrary(),
                 languages:Languages=Languages()):
        self.macro_library = macro_library
        self.languages = languages
        self._root_language = None

    def html_link_element(self, target, text):
        return html.a(text, href=target, class_="t4wiki-link")

    def register_language(self, language:Language):
        self.languages.register(language)

        if self._root_language is None:
            self._root_language = language

    def language_by_iso(self, iso:str):
        return self.languages.by_iso(iso)

    @property
    def root_language(self):
        if self._root_language is None:
            raise UnknownLanguage("No language specified, yet "
                                  "(no root lanuage).")
        return self._root_language

    @root_language.setter
    def root_language(self, language:Language):
        if language not in self.languages:
            raise UnknownLanguage(repr(language.iso) + " " +
                                  repr(self.languages))
        self._root_language = language
