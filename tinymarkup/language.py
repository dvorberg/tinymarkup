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


import re, dataclasses

from .exceptions import UnknownLanguage

## Languages
@dataclasses.dataclass
class Language(object):
    iso: str
    tsearch_configuration: str

    @property
    def config_string(self):
        return f"{self.iso}:{self.tsearch_configuration}"

    def __hash__(self):
        return hash(self.config_string)

    @property
    def ui_name(self):
        if self.tsearch_configuration == "simple":
            # This assumes you don't want languages selectable in the UI
            # that you didn’t bother to create a tsearch configuration for.
            return None
        else:
            # This is usually the English name for the language.
            # Use i18n to translate to usable values at template render time.
            return self.tsearch_configuration.capitalize()

config_string_re = re.compile(r"([a-z]{2}):([-_a-zA-Z0-9]+)(?:[,; ]+|$)")
class Languages(dict):
    def __init__(self, *languages):
        super().__init__()
        for language in languages:
            self.register(language)

    @classmethod
    def from_config_string(Languages, config):
        """
        Create a Languages object from a string representation typically
        used in config files and on the command line. Expects “iso:name” pairs
        with space, “,” or “;” as separators, as in:

           'en:english; de:german'

        """
        result = config_string_re.findall(config)
        langs = [ Language(iso, name) for iso, name in result ]
        return Languages(*langs)

    def register(self, language):
        self[language.iso] = language

    def by_iso(self, iso):
        try:
            return self[iso]
        except KeyError:
            raise UnknownLanguage(f"Unknown language (ISO) code: “{iso}”")

    def __contains__(self, language):
        if isinstance(language, Language):
            language = language.iso

        return super().__contains__(language)
