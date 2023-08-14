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


from .language import Languages
from .macro import MacroLibrary

## Context
class Context(object):
    def __init__(self, macro_library:MacroLibrary=MacroLibrary(),
                 languages:Languages=Languages()):
        self.macro_library = macro_library
        self.languages = languages

    def register_language(self, language):
        self.languages.register(language)

    def language(self, iso):
        return self.languages.by_iso(iso)
