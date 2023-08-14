"""
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

import dataclasses

## Languages
@dataclasses.dataclass
class Language(object):
    iso: str
    tsearch_configuration: str

class Languages(dict):
    def __init__(self, *languages):
        super().__init__()
        for language in languages:
            self.register(language)

    def register(self, language):
        self[language.iso] = language

    def by_iso(self, iso):
        try:
            return self[isi]
        except KeyError:
            raise UnknownLanguage(f"Unknown language (ISO) code: “{iso}”")
